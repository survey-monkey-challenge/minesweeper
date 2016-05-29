from django.core import signing
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import generic

from .models import Game, Difficulty
from .forms import CreateGameForm


# Not that this is really needed, but I'm making the url of every game unguessable
# by signing the game id (from the db). Another solution is to generate a uuid, save it
# in the model, index that field and use it to retrieve the game. I rather avoid that
# but I'm not 100% happy with this approach either
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
        if self.object.game_over:
            context_data['initial_timer'] = self.object.end_timer
        else:
            timer_delta = (timezone.now() - self.object.creation_datetime)
            context_data['initial_timer'] = int(timer_delta.total_seconds())
        return context_data
