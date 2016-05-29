import json

from django.core import signing
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views import generic

from .models import Game, Difficulty
from .forms import CreateGameForm


class CreateGameView(generic.FormView):
    form_class = CreateGameForm
    template_name = 'create_game.html'

    def form_valid(self, form):
        difficulty = Difficulty(int(form.cleaned_data['difficulty']))
        self.object = Game.create(difficulty=difficulty)
        return super().form_valid(form)

    def get_success_url(self):
        signer = signing.Signer()
        signed_id = signer.sign(self.object.id)
        return reverse('game:match', args=(signed_id,))


class GameView(generic.DetailView):
    object_name = 'game'
    template_name = 'game.html'

    def get_object(self, queryset=None):
        signer = signing.Signer()
        game_id = signer.unsign(self.kwargs['signed_id'])
        return get_object_or_404(Game, pk=int(game_id))

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['signed_id'] = self.kwargs['signed_id']
        context_data['form'] = CreateGameForm(
            action=reverse('game:create'),
            submit_label='Start new game'
        )
        return context_data


def sweep_view(request, signed_id):
    if not request.is_ajax() or not request.POST:
        raise HttpResponseBadRequest()

    signer = signing.Signer()
    game_id = signer.unsign(signed_id)
    game = get_object_or_404(Game, pk=game_id)
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    is_game_over, cells = game.reveal_area(x, y)
    data = {
        'is_game_over': is_game_over,
        'cells': [
            {
                'x': cell.x,
                'y': cell.y,
                'neighbor_mines': cell.neighbor_mines,
                'css_class': cell.display.name,
            } for cell in cells
        ]
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def flag_view(request, signed_id):
    if not request.is_ajax() or not request.POST:
        raise HttpResponseBadRequest()

    signer = signing.Signer()
    game_id = signer.unsign(signed_id)
    game = get_object_or_404(Game, pk=game_id)
    x = int(request.POST['x'])
    y = int(request.POST['y'])
    cells = game.flag(x, y)
    data = {
        'cells': [
            {
                'x': cell.x,
                'y': cell.y,
                'css_class': cell.display.name,
            } for cell in cells
        ]
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
