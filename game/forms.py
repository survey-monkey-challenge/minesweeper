from django import forms
from crispy_forms import helper, layout

from .models import Game


class CreateGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['difficulty']

    def __init__(self, *args, action='', **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-8'
        self.helper.field_class = 'col-md-4'
        self.helper.form_method = 'post'
        self.helper.form_action = action
        self.helper.add_input(layout.Submit('submit', 'Start new game'))
