import json

from django.core import signing
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from .models import Game


signer = signing.Signer()


def sweep_view(request, signed_id):
    return process_action_request(request, signed_id, Game.sweep_cell)


def flag_view(request, signed_id):
    return process_action_request(request, signed_id, Game.flag_cell)


def process_action_request(request, signed_id, action):
    '''
    Both sweep and flag actions are pretty much identical except for the method
    they call on the game model object.
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
                'html': render_to_string('cell.html', {'cell': cell})
            } for cell in cells
        ]
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
