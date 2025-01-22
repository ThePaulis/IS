from django.urls import path
from .views import PlayersView

urlpatterns = [
    path('player/', PlayersView.as_view(), name='player_list'),

]