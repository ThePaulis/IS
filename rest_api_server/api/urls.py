from django.urls import path
from api.views.file_views import FileUploadView
from api.views.users import GetAllUsers

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload-file'),
    path('users/', GetAllUsers.as_view(), name='get-all-users')
]