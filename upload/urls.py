from django.urls import path, include 
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_document, name='upload'),
    #path('documents/', views.uploaded_documents, name='uploaded_documents'),
    path('logs-history/', views.logs_history, name='logs_history'),
    path('api/ask/', views.ask_question, name='ask_question'),
    path('logout/', views.logout_view, name='logout'),
    path('update/<int:doc_id>/', views.update_document, name='update_document'),
    path('delete/<int:doc_id>/', views.delete_document, name='delete_document'),
    path('health/', views.health_check, name='health_check'),
    path('auth/', include('social_django.urls', namespace='social')),
]
