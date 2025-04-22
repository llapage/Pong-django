from django.urls import path
from . import views

urlpatterns = [
    path("invite/<int:targetUserId>/", views.invite, name='invite'),
    path("accept/<int:requestId>/", views.accept, name='accept'),
    path("reject/<int:requestId>/", views.reject, name='reject'),
    path("remove/<int:targetUserId>/", views.remove, name='remove'),
    path("block/<int:targetUserId>/", views.block, name='block'),
    path("unblock/<int:targetUserId>/", views.unblock, name='unblock'),
    path("getOnlinePlayers/", views.getOnlinePlayers, name='getOnlinePlayers'),
    path("getOnlineFriends/", views.getOnlineFriends, name='getOnlineFriends'),
    path("getOnlineStrangers/", views.getOnlineStrangers, name='getOnlineStrangers'),
    path("getFriends/", views.getFriends, name='getFriends'),
    path("getBlockedUsers/", views.getBlockedUsers, name='getBlockedUsers'),
    path("inFriendRequests/", views.inFriendRequests, name='inFriendRequests'),
    path("isBlocked/<int:targetUserId>/", views.is_blocked, name='is_blocked'), #deprecated
    path("socialStatus/<int:targetUserId>/", views.social_status, name='social_status'),
]