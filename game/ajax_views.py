import json

from django.core import signing
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from .models import Game


signer = signing.Signer()


def sweep_view(request, signed_id):
    return process_action_request(request, signed_id, Game.sweep_cell, False)


def flag_view(request, signed_id):
    return process_action_request(request, signed_id, Game.flag_cell, True)


def process_action_request(request, signed_id, action, hide_mine_counter=True):
    '''
    Both sweep and flag actions are pretty much identical except for the method
    they call on the game model object, and whether it should return nearby_mine_counter.
    That's why this function was created. It can be seem as a higher-order function.
    '''
    if not request.is_ajax() or not request.POST:
        return HttpResponseBadRequest()

    game_id = signer.unsign(signed_id)
    game = get_object_or_404(Game, pk=game_id)
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    is_game_over, win, cells = action(game, x, y)
    data = {
        'is_game_over': is_game_over,
        'win': win,
        'cells': [
            {
                'x': cell.x,
                'y': cell.y,
                'nearby_mine_counter': cell.nearby_mine_counter if not hide_mine_counter else None,
                'css_class': cell.display.name,
            } for cell in cells
        ]
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
