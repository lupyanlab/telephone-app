import json
from unipath import Path
import StringIO
import zipfile

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from .models import Game, Chain, Message
from .forms import NewGameForm, UploadMessageForm

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

class UploadMessageView(UpdateView):
    model = Message
    form_class = UploadMessageForm
    template_name = 'grunt/upload-message.html'

    def get_form(self, form_class):
        """ Populate the form's action attribute with the correct url """
        form = super(UploadMessageView, self).get_form(form_class)
        form.helper.form_action = reverse('upload', kwargs = {'pk': form.instance.pk})
        return form

class CompletionView(DetailView):
    template_name = 'grunt/complete.html'
    model = Game

    def get_context_data(self, **kwargs):
        context_data = super(CompletionView, self).get_context_data(**kwargs)
        game = context_data['game']
        message_receipts = self.request.session.get('messages', list())
        receipt_code = '-'.join(map(str, message_receipts))
        completion_code = 'G{pk}-{receipts}'.format(pk = game.pk,
                                                    receipts = receipt_code)
        context_data['completion_code'] = completion_code
        return context_data

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
    request.session['messages'] = request.session.get('messages', list())
    try:
        chain = game.pick_next_chain(request.session['receipts'])
        message = chain.select_empty_message()
    except Chain.DoesNotExist:
        # It's likely that this player has already played the game
        # and returned to play it again without clearing the session.
        return redirect('complete', pk = game.pk)
    except Message.DoesNotExist:
        # something weird happened
        raise Http404("The game is not configured properly.")

    return render(request, 'grunt/play.html', {'game': game, 'message': message})

@require_POST
def accept(request, pk):
    request.session['instructed'] = True
    return redirect('play', pk = pk)

@require_POST
def clear(request, pk):
    request.session['instructed'] = False
    request.session['receipts'] = list()
    request.session['messages'] = list()
    return redirect('complete', pk = pk)


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
        message.audio = request.FILES.get('audio', None)
        if not message.audio:
            raise Http404('No message attached to post')

        message.save()
        message.replicate()

        # Add the successful message chain to session receipts
        receipts = request.session.get('receipts', list())
        receipts.append(message.chain.pk)
        request.session['receipts'] = receipts

        # Add the message to the message receipts
        message_receipts = request.session.get('messages', list())
        message_receipts.append(message.pk)
        request.session['messages'] = message_receipts

        # Search for the next message
        game = message.chain.game
        next_chain = game.pick_next_chain(receipts)
        next_message = next_chain.select_empty_message()

        data = {'message': next_message.pk}
        if next_message.parent and next_message.parent.audio:
            data['src'] = next_message.parent.audio.url
    except Message.DoesNotExist:
        # Something weird happened.
        data = {}
    except Chain.DoesNotExist:
        # There are no more chains for this player to respond to.
        # Returning an empty response will redirect the player
        # to the completion page.
        data = {}

    return JsonResponse(data)

class InspectView(DetailView):
    template_name = 'grunt/inspect.html'
    model = Game

@require_GET
def message_data(request, pk):
    game = Game.objects.get(pk = pk)
    ordered_chain_set = game.chain_set.all().order_by('pk')
    requested_chain_ix = int(request.GET['chain'])
    requested_chain = ordered_chain_set[requested_chain_ix]
    message_data = requested_chain.nest()
    return JsonResponse(json.dumps(message_data), safe = False)

@require_POST
def sprout(request, pk):
    message = get_object_or_404(Message, pk = pk)
    message.replicate()

    message_data = message.chain.nest()
    return JsonResponse(json.dumps(message_data), safe = False)

@require_POST
def close(request, pk):
    message = get_object_or_404(Message, pk = pk)
    chain = message.chain
    message.delete()

    message_data = chain.nest()
    return JsonResponse(json.dumps(message_data), safe = False)

def download(request):
    selection_query = request.POST['selection']
    selection_str = selection_query.split(',')
    selection = map(int, selection_str)
    messages = Message.objects.filter(id__in = selection)

    s = StringIO.StringIO()
    zf = zipfile.ZipFile(s, "w")

    # Name the root directory in the zip based on the game name
    root_dirname = messages[0].chain.game.dirname()

    for msg in messages:
        audio_path = msg.audio.path

        msg_name_format = "{generation}-{parent}-{message}.wav"
        msg_name_kwargs = {}
        msg_name_kwargs['generation'] = 'gen' + str(msg.generation)
        msg_name_kwargs['message'] = 'message' + str(msg.id)

        if not msg.parent:
            msg_name_kwargs['parent'] = 'seed'
        else:
            msg_name_kwargs['parent'] = 'parent' + str(msg.parent.id)

        msg_name = msg_name_format.format(**msg_name_kwargs)
        msg_path = Path(root_dirname, msg_name)

        zf.write(audio_path, msg_path)

    zf.close()

    response = HttpResponse(s.getvalue(), content_type = 'application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename="messages.zip"'
    return response
