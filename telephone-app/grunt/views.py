import json

from django.core import serializers
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from .models import Game, Chain, Message
from .forms import NewGameForm, UpdateMessageForm, ResponseForm

class GameListView(ListView):
    template_name = 'grunt/games.html'
    model = Game

    def get_queryset(self):
        """ Show active games with newest games first """
        active_games = self.model._default_manager.filter(status = 'ACTIV')
        newest_first = active_games.order_by('-id')
        return newest_first

class NewGameView(CreateView):
    template_name = 'grunt/new-game.html'
    form_class = NewGameForm
    success_url = '/'

    def form_valid(self, form):
        form.save()
        return super(NewGameView, self).form_valid(form)

@require_GET
def play_game(request, pk):
    """ Determine what to do when a user requests the game page.

    Outcomes
    --------
    1. First time users should get the instructions page.
    2. Instructed users should get an entry form with the first
       message rendered in the template.
    """
    game = get_object_or_404(Game, pk = pk)

    request.session['instructed'] = request.session.get('instructed', False)

    if not request.session['instructed']:
        return render(request, 'grunt/instruct.html', {'game': game})

    request.session['receipts'] = request.session.get('receipts', list())
    try:
        chain = game.pick_next_chain(request.session['receipts'])
        message = chain.select_empty_message()
    except Chain.DoesNotExist:
        # something weird happened
        # Player returned to the game?
        return redirect('complete', pk = game.pk)
    except Message.DoesNotExist:
        # something weird happened
        raise Http404("No empty messages were found in the chain")

    return render(request, 'grunt/play.html', {'game': game, 'message': message})

@require_POST
def accept(request, pk):
    request.session['instructed'] = True
    return redirect('play', pk = pk)

@require_POST
def clear(request, pk):
    request.session['receipts'] = list()
    return redirect('play', pk = pk)

@require_POST
def respond(request):
    pk = request.POST['message']
    try:
        message = Message.objects.get(pk = pk)

        # If the message already has an audio file, (i.e., someone
        # has already submitted a response), then create a new
        # branch from the parent, and add the new audio to that.
        if message.audio:
            parent = message.parent
            message = parent.replicate()

        # Update the message with the newly recorded audio
        message.audio = request.FILES['audio']
        message.save()
        message.replicate()

        # Add the successful message chain to session receipts
        receipts = request.session.get('receipts', list())
        receipts.append(message.chain.pk)
        request.session['receipts'] = receipts

        # Search for the next message
        game = message.chain.game
        next_chain = game.pick_next_chain(receipts)
        next_message = next_chain.select_empty_message()

        data = {'message': next_message.pk}
        if next_message.parent and next_message.parent.audio:
            data['src'] = next_message.parent.audio.url
    except Message.DoesNotExist:
        # something weird happened
        data = {}
    except Chain.DoesNotExist:
        # player is done
        data = {}

    return JsonResponse(data)

class CompletionView(DetailView):
    template_name = 'grunt/complete.html'
    model = Game

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
