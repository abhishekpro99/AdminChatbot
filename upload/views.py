#upload/views.py

import os
import json
import fitz  # PyMuPDF
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance, VectorParams, Filter, FieldCondition, MatchValue
from qdrant_client.models import PointIdsList

from .models import Document, QuestionLog, DocumentType
from .forms import DocumentForm, DocumentUpdateForm
from . import llama_setup  # Configures LLM

from llama_index.core import Settings
from llama_index.core.llms import ChatMessage

# Load environment variables
load_dotenv()

# Sentence Transformer model
model = SentenceTransformer("BAAI/bge-small-en-v1.5", cache_folder="/tmp/huggingface_cache")


# Qdrant setup
collection_name = "documents"
vector_size = 384
qdrant_client = QdrantClient(url="http://localhost:6333")

# -----------------------------------
@csrf_exempt
def ask_question(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)

    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        user_id = data.get('user_id')

        if not question:
            return JsonResponse({'error': 'Question cannot be empty.'}, status=400)

        embedding = model.encode(question).tolist()

        search_result = qdrant_client.search(
            collection_name=collection_name,
            query_vector=embedding,
            limit=1,
            with_payload=True
        )

        matched_doc_id = None
        matched_user = None
        matched_role = None
        context_text = ""
        answer = ""

        if search_result:
            best_match = search_result[0]
            matched_doc_id = best_match.id
            payload = best_match.payload
            matched_user = payload.get("username")
            matched_role = payload.get("role")
            context_text = payload.get("content", "").strip()

        if not context_text:
            answer = "Matched document has no content."
        else:
            prompt = [
                ChatMessage(role="system", content="You are an assistant answering questions using the context."),
                ChatMessage(role="user", content=f"Context:\n{context_text}"),
                ChatMessage(role="user", content=f"Question: {question}")
            ]
            response = Settings.llm.chat(messages=prompt)
            answer = str(response)

        user = User.objects.filter(id=user_id).first() if user_id else None
        qlog = QuestionLog.objects.create(
            user=user,
            question=question,
            answer=answer,
            matched_doc_id=matched_doc_id
        )

        return JsonResponse({
            'answer': answer,
            'matched_doc_id': matched_doc_id,
            'matched_user': matched_user,
            'role': matched_role,
            'user_id': user_id,
            'question_log_id': qlog.id,
            'show_notify_option': answer.startswith("Matched document has no content.") or answer.startswith("No relevant document found.")
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# -----------------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/dashboard/')
        return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

@login_required(login_url='/')
def dashboard(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect(reverse('login'))

# -----------------------------------
@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            uploaded_file = request.FILES['file']
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()

            # Static metadata
            document.name = "Static Name"
            document.username = "StaticUsername"
            document.role = "Admin"
            document.file = uploaded_file

            # Additional fields
            document.title = request.POST.get('title')
            document.department = request.POST.get('department')
            document.effective_date = request.POST.get('effective_date')
            document.expiration_date = request.POST.get('expiration_date')
            document.version = request.POST.get('version')
            document.owner = request.POST.get('owner')
            document.summary = request.POST.get('summary')
            document.tags = request.POST.get('tags')
            doc_type_id = request.POST.get('doc_type')
            if doc_type_id:
                document.doc_type = DocumentType.objects.get(id=doc_type_id)
            document.save()

            file_content = ""
            try:
                if file_ext == '.pdf':
                    uploaded_file.seek(0)
                    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf:
                        for page in pdf:
                            file_content += page.get_text()
                elif file_ext == '.txt':
                    uploaded_file.seek(0)
                    file_content = uploaded_file.read().decode('utf-8', errors='ignore')
                else:
                    messages.warning(request, f"Unsupported file type: {file_ext}")
                    return redirect('upload')
            except Exception as e:
                messages.error(request, f"Error reading file: {e}")
                return redirect('upload')

            if not file_content.strip():
                messages.warning(request, "No text content found in file.")
                return redirect('upload')

            embedding = model.encode(file_content).tolist()

            if not qdrant_client.collection_exists(collection_name):
                qdrant_client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )

            try:
                qdrant_client.upsert(
                    collection_name=collection_name,
                    points=[PointStruct(
                        id=document.id,
                        vector=embedding,
                        payload={
                            "username": document.username,
                            "role": document.role,
                            "content": file_content[:3000]
                        }
                    )]
                )
                messages.success(request, "Document uploaded and embedded successfully.")
            except Exception as e:
                messages.error(request, f"Qdrant insert failed: {e}")
            return redirect('upload')

    form = DocumentForm()
    documents = Document.objects.filter(is_deleted=False).order_by('-uploaded_at')
    document_types = DocumentType.objects.all()
    return render(request, 'upload.html', {
        'form': form,
        'documents': documents,
        'document_types': document_types
    })

# -----------------------------------
@login_required
def update_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    old_file = document.file.path if document.file else None

    if request.method == 'POST':
        form = DocumentUpdateForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            updated_doc = form.save(commit=False)
            new_file = request.FILES.get('file')

            if new_file:
                if not new_file.name.lower().endswith('.pdf'):
                    messages.error(request, "Only PDF files are supported.")
                    return render(request, 'update_document.html', {'form': form, 'document': document})

                updated_doc.file = new_file
                updated_doc.save()

                try:
                    file_path = updated_doc.file.path
                    full_text = ""
                    with fitz.open(file_path) as pdf:
                        for page in pdf:
                            full_text += page.get_text()

                    if not full_text.strip():
                        raise ValueError("No content extracted.")

                    vector = model.encode(full_text, normalize_embeddings=True).tolist()
                    qdrant_client.upsert(
                        collection_name=collection_name,
                        points=[PointStruct(
                            id=int(doc_id),
                            vector=vector,
                            payload={
                                "username": request.user.username,
                                "role": "Admin",
                                "content": full_text
                            }
                        )]
                    )

                    messages.success(request, "Document updated successfully.")
                    return HttpResponseRedirect(reverse('upload') + '?updated=1')

                except Exception as e:
                    updated_doc.file = None
                    updated_doc.save()
                    messages.error(request, f"Failed to re-index: {e}")
            else:
                updated_doc.save()
                messages.success(request, "Document updated.")
                return redirect('upload')
    else:
        form = DocumentUpdateForm(instance=document)

    return render(request, 'update_document.html', {
        'form': form,
        'document': document
    })

# -----------------------------------
@login_required
@csrf_exempt
def delete_document(request, doc_id):
    if request.method == 'POST':
        document = get_object_or_404(Document, id=doc_id)

        qdrant_client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(points=[document.id])
        )

        document.is_deleted = True
        document.save()

        return JsonResponse({'message': 'Document deleted successfully.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# -----------------------------------
@login_required
def logs_history(request):
    logs = QuestionLog.objects.all().order_by('-created_at')
    return render(request, 'logs_history.html', {'logs': logs})


@login_required
def upload_success(request):
    return render(request, 'upload_success.html')



# upload/views.py
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("App is up.")
