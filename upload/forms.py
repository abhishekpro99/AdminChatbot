from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file','doc_type']  # Only display file field on the form
      #  fields = ['name', 'username', 'file', 'role']

class DocumentUpdateForm(forms.ModelForm):
    effective_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    expiration_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Document
        fields = [
            'title', 'doc_type', 'role', 'file', 'department', 'effective_date',
            'expiration_date', 'version', 'owner', 'summary', 'tags'
        ]