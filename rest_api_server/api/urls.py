from django.urls import path
from .views.file_views import FileUploadView
from .views.sales import GetAllSales
from .views.files import GetAllFiles

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload-file'),
    path('sales/', GetAllSales.as_view(), name='sales')
    path('files/', GetAllFiles.as_view(), name='files')

]
