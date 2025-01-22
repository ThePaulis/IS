from django.urls import path
from .views import PlayersView, PlayersByCountryView

urlpatterns = [
    path('players/', PlayersView.as_view(), name='warehouses_list'),
    path('playersByCountry/', PlayersByCountryView.as_view(), name='warehouses_list'),

]