from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('', views.upload_document, name='upload_document'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/ask/', views.ask_question, name='ask_question'),
    path('logout/', views.logout_view, name='logout'),
    path('documents/', views.uploaded_documents, name='uploaded_documents'),
    path('logs-history/', views.logs_history, name='logs_history'),
   # path('success/', views.upload_success, name='upload_success'),
    path('update/<int:doc_id>/', views.update_document, name='update_document'),

]
