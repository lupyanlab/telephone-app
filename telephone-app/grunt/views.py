import json

from django.core import serializers
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import View, ListView, FormView, DetailView, UpdateView

from .models import Game, Chain, Message
from .forms import NewGameForm, UpdateMessageForm, ResponseForm

class GamesView(ListView):
    template_name = 'grunt/games.html'
    model = Game

    def get_queryset(self):
        """ Show active games with newest games first """
        active_games = self.model._default_manager.filter(status = 'ACTIV')
        newest_first = active_games.order_by('-id')
        return newest_first

class NewGameView(FormView):
    template_name = 'grunt/new-game.html'
    form_class = NewGameForm
    success_url = '/games/'

    def form_valid(self, form):
        form.save()
        return super(NewGameView, self).form_valid(form)

class PlayView(View):
    def get(self, request, pk):
        """ Determine what to do when a user requests the game page.

        Outcomes
        --------
        1. First time users should get the instructions page.
        2. Instructed users should get an entry form.
        3. Completed users should get a completion page.
        """
        self.game = get_object_or_404(Game, pk = pk)

        instructed = request.session.get('instructed', False)
        request.session['instructed'] = instructed

        if not instructed:
            return self.instruct(request)

        receipts = request.session.get('receipts', list())
        request.session['receipts'] = receipts

        try:
            rendered_response = self.play(request)
        except Chain.DoesNotExist:
            rendered_response = self.complete(request)

        return rendered_response

    def instruct(self, request):
        """ Render the instructions for the telephone game """
        return render(request, 'grunt/instruct.html', {'game': self.game})

    def play(self, request):
        """ Render an entry form for a chain not already in the session.

        Raises an exception (Chain.DoesNotExist) if there are no more
        chains.
        """
        context_data = {}
        context_data['game'] = self.game

        receipts = request.session['receipts']
        chain = self.game.pick_next_chain(receipts)
        message = chain.select_empty_message()
        context_data['message'] = message

        form = ResponseForm(initial = {'message': message.pk})
        context_data['form'] = form

        return render(request, 'grunt/play.html', context_data)

    def post(self, request, pk):
        """ Determine what to do with an entry.

        A valid entry appends a receipt to the session, and tries to get
        the next form. Otherwise, pass back the same form with validation
        errors.

        Outcomes
        --------
        1. If available, play the next cluster.
        2. If not, get the completion page.
        3. If the entry didn't work, render the errors.
        """
        self.game = get_object_or_404(Game, pk = pk)

        form = ResponseForm(data = request.POST, files = request.FILES)

        if form.is_valid():
            message = form.save()

            receipts = request.session.get('receipts', list())
            receipts.append(message.chain.pk)
            request.session['receipts'] = receipts

            return self.get(request, pk)
        else:
            message_pk = form.cleaned_data['message']
            message = Message.objects.get(pk = message_pk)

            context_data = {
                'game': self.game,
                'message': message,
                'form': form,
            }

            return render(request, 'grunt/play.html', context_data)

    def complete(self, request):
        return render(request, 'grunt/complete.html', {'game': self.game})

class InspectView(DetailView):
    template_name = 'grunt/inspect.html'
    model = Game

@require_GET
def message_data(request, pk):
    game = Game.objects.get(pk = pk)
    chain_set = game.chain_set.all()
    chain_set_dicts = [chain.to_dict() for chain in chain_set]
    chain_set_json = json.dumps(chain_set_dicts)
    return JsonResponse(chain_set_json, safe = False)

class MessageView(DetailView):
    template_name = 'grunt/edit.html'
    model = Message

@require_POST
def accept(request, pk):
    request.session['instructed'] = True
    return redirect('play', pk = pk)

@require_POST
def clear(request, pk):
    request.session['receipts'] = list()
    return redirect('play', pk = pk)

@require_POST
def sprout(request, pk):
    message = get_object_or_404(Message, pk = pk)
    message.replicate()

    game_url = message.chain.game.get_inspect_url()
    return redirect(game_url)

@require_POST
def close(request, pk):
    message = get_object_or_404(Message, pk = pk)
    message.delete()

    game_url = message.chain.game.get_inspect_url()
    return redirect(game_url)

class UploadMessageView(UpdateView):
    model = Message
    form_class = UpdateMessageForm
    template_name = 'grunt/upload-message.html'
