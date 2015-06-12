from django import forms
from django.core.urlresolvers import reverse

from .models import Game, Chain, Message

class NewGameForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = ('name', )

    def save(self, *args, **kwargs):
        game = super(NewGameForm, self).save(*args, **kwargs)
        chain = game.chain_set.create()
        message = chain.message_set.create()
        return game

class UploadMessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('audio', )

    def save(self, *args, **kwargs):
        message = super(UploadMessageForm, self).save(*args, **kwargs)
        message.replicate()
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
