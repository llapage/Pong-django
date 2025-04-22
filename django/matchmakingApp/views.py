# Create your views here.

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .users import Users

@login_required
def check_game_status(request):
    user_id = request.user.id
    in_game = Users.is_in_game(user_id)
    return JsonResponse({"in_game": in_game})

@login_required
def check_tournament_status(request):
    user_id = request.user.id
    in_tournament = Users.is_in_tournament(user_id)
    return JsonResponse({"in_tournament": in_tournament})
