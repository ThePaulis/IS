from django.urls import path
from .views import WarehousesView

urlpatterns = [
    path('warehouses/', WarehousesView.as_view(), name='warehouses_list'),
]