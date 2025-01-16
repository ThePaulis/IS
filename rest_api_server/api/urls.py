from django.urls import path
from .views.file_views import FileUploadView, GetSubXmlWarehouseView, FileUploadChunksView, GetSubXmPaymentMethodView, GetSubXmlProductLine
from .views.sales import GetAllSales
from .views.files import GetAllFiles

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload-file'),
    path('sales/', GetAllSales.as_view(), name='sales'),
    path('files/', GetAllFiles.as_view(), name='files'),
    path('subxml-warehouse-sales/', GetSubXmlWarehouseView.as_view(), name='get-subxml'),
    path('upload-file/by-chunks', FileUploadChunksView.as_view(), name='upload-file-by-chunks'),
    path('subxml-payment-method/', GetSubXmPaymentMethodView.as_view(), name='get-subxml-payment-method'),
    path('subxml-product-line/', GetSubXmlProductLine.as_view(), name='get-subxml-product-line'),
]