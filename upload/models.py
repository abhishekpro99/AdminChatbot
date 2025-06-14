from django.db import models
from django.contrib.auth.models import User

# ✅ Master table for Document Types
class DocumentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    
class Document(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)       # Static value
    username = models.CharField(max_length=255)                          # Static value
    file = models.FileField(upload_to='documents/')
    doc_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True)      # Travel Policy, etc.
    role = models.CharField(max_length=100)              # Static role
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # ✅ Newly Added Fields:
    title = models.CharField(max_length=255, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    version = models.CharField(max_length=50, null=True, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False) 
    def __str__(self):
        return self.name or self.title or self.file.name



class QuestionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    question = models.TextField()
    answer = models.TextField(blank=True)
    matched_doc_id = models.IntegerField(null=True, blank=True)
    notify_admin = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question[:50]}..."

