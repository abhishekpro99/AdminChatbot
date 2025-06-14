from django.contrib import admin
from django.urls import path
from upload.views import login_view, upload_document, upload_success,dashboard,logout_view,delete_document,ask_question,logs_history,update_document

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'), 
    #path('upload/', upload_document, name='upload'),  
    path('logs_history/', logs_history, name='logs_history'),  
    path('dashboard/', dashboard, name='dashboard'), 
    path('logout/', logout_view, name='logout'), 
    #path('success/', upload_success, name='upload_success'),
    path('delete/<int:doc_id>/', delete_document, name='delete_document'),
    path('update_document/<int:doc_id>/', update_document, name='update_document'),
    path('dashboard/', dashboard, name='dashboard'), 
    path('api/ask/', ask_question, name='ask_question'),
    
]
