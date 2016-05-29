from django.core import signing
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views import generic

from .models import Game, Difficulty
from .forms import CreateGameForm


signer = signing.Signer()


class CreateGameView(generic.FormView):
    form_class = CreateGameForm
    template_name = 'create_game.html'

    def form_valid(self, form):
        difficulty = Difficulty(int(form.cleaned_data['difficulty']))
        self.object = Game.create(difficulty=difficulty)
        return super().form_valid(form)

    def get_success_url(self):
        signed_id = signer.sign(self.object.id)
        return reverse('game:match', args=(signed_id,))


class RankingView(generic.TemplateView):
    template_name = 'ranking.html'


class GameView(generic.DetailView):
    object_name = 'game'
    template_name = 'game.html'

    def get_object(self, queryset=None):
        game_id = signer.unsign(self.kwargs['signed_id'])
        return get_object_or_404(Game, pk=int(game_id))

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['signed_id'] = self.kwargs['signed_id']
        context_data['form'] = CreateGameForm(
            action=reverse('game:create'),
            initial={'difficulty': self.object.difficulty}
        )
        return context_data
