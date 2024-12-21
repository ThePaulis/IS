from django.urls import path
from .views.file_views import FileUploadView, GetSubXmlView, FileUploadChunksView
from .views.sales import GetAllSales
from .views.files import GetAllFiles

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload-file'),
    path('sales/', GetAllSales.as_view(), name='sales'),
    path('files/', GetAllFiles.as_view(), name='files'),
    path('subxml-warehouse-sales/', GetSubXmlView.as_view(), name='get-subxml'),
    path('upload-file/by-chunks', FileUploadChunksView.as_view(), name='upload-file-by-chunks'),
]