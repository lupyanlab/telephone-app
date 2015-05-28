from django import forms
from django.core.urlresolvers import reverse

from .models import Game, Chain, Message

class NewGameForm(forms.ModelForm):
    pass
    # class Meta:
    #     model = Game
    #     fields = ('name', )

class ResponseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ResponseForm, self).__init__(*args, **kwargs)
        self.fields['audio'].required = True

    class Meta:
        model = Message
        fields = ('parent', 'audio')

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

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('chain', 'audio')

# class MessageForm(forms.ModelForm):
#
#     class Meta:
#         model = Message
#         fields = ('chain', 'parent', 'audio')
#         widgets = {
#             'chain': forms.TextInput(),
#             'parent': forms.TextInput(),
#         }
#         error_messages = {
#             'content': {
#                 'required': "You didn't make a recording",
#             },
#         }
#
#     def __init__(self, receipts = list(), *args, **kwargs):
#         super(MessageForm, self).__init__(*args, **kwargs)
#         self.receipts = receipts
#
#     def game(self):
#         return self.instance.chain.game
#
#     def parent_url(self):
#         return self.instance.parent.audio.url
#
#     def status(self):
#         kwargs = {}
#         kwargs['current'] = len(self.receipts) + 1
#         kwargs['total'] = self.game().chain_set.count()
#         return "Message {current} of {total}".format(**kwargs)
#
#     def as_context(self):
#         context = {
#             'chain': self.instance.chain.pk,
#             'parent': self.instance.parent.pk,
#             'url': self.instance.parent.audio.url,
#             'status': self.status(),
#         }
#         return context
