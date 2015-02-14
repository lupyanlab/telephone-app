import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.core.urlresolvers import reverse
# from django.http import JsonResponse
from django.http import HttpResponse
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import View, DetailView, ListView

from .models import Game, Seed, Cluster, Entry
from .forms import EntryForm

class GameListView(ListView):
    template_name = 'telephone/list.html'
    model = Game

class CompleteView(DetailView):
    template_name = 'telephone/complete.html'
    model = Game

class PlayGameView(View):
    template_name = 'telephone/game.html'

    def get(self, request, pk):
        """ Determine what to do when a user requests the game page.

        Outcomes
        --------
        1. First time users should see the instructions page.
        2. Instructed users should see an entry form.
        3. Completed users should see a completion code.
        """
        self.game = get_object_or_404(Game, pk = pk)

        receipts = request.session.get('receipts', list())
        request.session['receipts'] = receipts

        try:
            form = self.get_form(receipts)
            return render(request, self.template_name, {'form': form})
        except Cluster.DoesNotExist:
            return redirect('complete', pk = pk)

    def post(self, request, pk):
        """ Validate the entry

        A valid entry appends a receipt to the session, and redirects to get
        the next form. Otherwise, pass back the same form with validation
        errors.
        """
        self.game = get_object_or_404(Game, pk = pk)

        form = EntryForm(data = request.POST, files = request.FILES)

        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def get_complete(self):
        pass

    def get_form(self, receipts):
        """ Create an entry form for a cluster not already in the session.

        Raises a Cluster.DoesNotExist if there are no more clusters.
        """
        entry = self.game.prepare_entry(receipts)
        form = EntryForm(instance = entry, receipts = receipts)
        return form

    def form_valid(self, form, request):
        """ """
        entry = form.save()

        receipts = request.session.get('receipts', list())
        receipts.append(entry.chain.cluster.pk)
        request.session['receipts'] = receipts

        try:
            form = self.get_form(receipts)
            if request.is_ajax():
                return HttpResponse(json.dumps(form.as_context()),
                        content_type = 'application/json')
            else:
                return render(request, self.template_name, {'form': form})
        except Cluster.DoesNotExist:
            if request.is_ajax():
                return HttpResponse(json.dumps(form.as_redirect()),
                    content_type = 'application/json')
            else:
                return redirect('complete', pk = self.game.pk)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

@require_POST
def clear_view(request, pk):
    request.session['receipts'] = list()

    if request.is_ajax():
        game = Game.objects.get(pk = pk)
        return HttpResponse(json.dumps({'complete': game.get_absolute_url()}),
            content_type = 'application/json')
    else:
        return redirect('game', pk = pk)
