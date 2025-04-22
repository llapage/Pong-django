from django.urls import path
from . import views

urlpatterns = [
	path("getGames/<int:targetUserId>/", views.get_games, name="get_games"),
    path("getGames/", views.get_games, name="get_games"),
    path("saveFakeGame/", views.save_fake_game, name='save_fake_game'),
]