from django import forms
from django.core.urlresolvers import reverse

from .models import Entry

class EntryForm(forms.ModelForm):

    class Meta:
        model = Entry
        fields = ('chain', 'parent', 'content')
        widgets = {
            'chain': forms.TextInput(),
            'parent': forms.TextInput(),
        }
        error_messages = {
            'content': {
                'required': "You didn't make a recording",
            },
        }

    def __init__(self, receipts = [], *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.receipts = receipts

    def game(self):
        return self.instance.chain.cluster.game

    def parent_url(self):
        return self.instance.parent.content.url

    def status(self):
        kwargs = {}
        kwargs['current'] = len(self.receipts) + 1
        kwargs['total'] = self.game().cluster_set.count()
        return "Message {current} of {total}".format(**kwargs)

    def as_context(self):
        context = {
            'chain': self.instance.chain.pk,
            'parent': self.instance.parent.pk,
            'url': self.instance.parent.content.url,
            'status': self.status(),
        }
        return context

    def as_redirect(self):
        game_complete = reverse('complete', kwargs = {'pk': self.game().pk})
        return {'complete': game_complete}
