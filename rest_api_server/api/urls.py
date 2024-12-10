from django.urls import path
from .views.file_views import FileUploadView
from .views.files import GetAllFiles

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload-file'),
    path('files/', GetAllFiles.as_view(), name='files')
]
