from django import forms
from django.core.urlresolvers import reverse

from .models import Game, Chain, Message

class NewGameForm(forms.ModelForm):
    num_chains = forms.IntegerField(initial = 1, min_value = 1)

    class Meta:
        model = Game
        fields = ('name', )

    def save(self, *args, **kwargs):
        game = super(NewGameForm, self).save(*args, **kwargs)

        for _ in range(self.cleaned_data['num_chains']):
            chain = game.chain_set.create()
            message = chain.message_set.create()

        return game

class UploadMessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('audio', )

    def save(self, *args, **kwargs):
        message = super(UploadMessageForm, self).save(*args, **kwargs)
        return message

class ResponseForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('parent', 'audio')

    def __init__(self, *args, **kwargs):
        super(ResponseForm, self).__init__(*args, **kwargs)
        self.fields['audio'].required = True

    def clean(self, *args, **kwargs):
        """ Associate the new message with the same chain as the parent """
        super(ResponseForm, self).clean(*args, **kwargs)
        parent = self.cleaned_data['parent']
        self.instance.chain = parent.chain

    def as_dict(self):
        parent = self.instance.parent
        context = {
            'parent': parent.pk,
            'url': parent.audio.url,
        }
