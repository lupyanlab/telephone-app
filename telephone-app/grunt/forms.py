from django import forms
from django.core.exceptions import ValidationError
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
    message = forms.IntegerField(required = False)

    class Meta:
        model = Message
        fields = ('audio', )

    def clean(self):
        cleaned_data = super(ResponseForm, self).clean()
        if cleaned_data['message']:
            self.instance = Message.objects.get(pk = cleaned_data['message'])

    def save(self, *args, **kwargs):
        message = super(ResponseForm, self).save(*args, **kwargs)
        message.replicate()
        return message

    def as_dict(self):
        parent = self.instance.parent
        context = {
            'parent': parent.pk,
            'url': parent.audio.url,
        }
