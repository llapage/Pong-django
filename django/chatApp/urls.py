from django.urls import path
from . import views

urlpatterns = [
    path("getRoom/<int:targetUserId>/", views.get_room, name='get_room'),
    path("chat/<int:targetUserId>/", views.get_room, name="get_room"),
    path("friends/<int:friendsID>/", views.friends, name='friends'),
]