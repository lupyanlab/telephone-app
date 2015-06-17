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

class UpdateMessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('audio', )

    def save(self, *args, **kwargs):
        message = super(UpdateMessageForm, self).save(*args, **kwargs)
        message.replicate()
        return message

class ResponseForm(forms.Form):
    message = forms.IntegerField(required = False)
    audio = forms.FileField(required = True)

    def save(self):
        super(ResponseForm, self).is_valid()
        message_pk = self.cleaned_data['message']
        message = Message.objects.get(pk = message_pk)

        if message.audio != '':
            if message.parent:
                message = message.parent.replicate()
            else:
                # Message has no parent, so overwriting audio
                pass
        else:
            # Message has no audio, so update as normal
            pass

        audio_file = self.cleaned_data['audio']
        model_form = UpdateMessageForm(instance = message,
                                       files = {'audio': audio_file})
        return model_form.save()
