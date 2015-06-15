
from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from unipath import Path
from model_mommy import mommy

from grunt.forms import NewGameForm, ResponseForm
from grunt.models import Game, Chain, Message

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class ViewTest(TestCase):
    def setUp(self):
        self.audio_path = Path(
            settings.APP_DIR,
            'grunt/tests/media/test-audio.wav')

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()

    def make_session(self, game, instructed = False, receipts = list()):
        self.client.get(game.get_absolute_url())
        session = self.client.session
        session['receipts'] = receipts
        session['instructed'] = instructed
        session.save()


class GamesViewTest(ViewTest):
    """ Show all available games """
    def test_game_list_view_renderes_game_list_template(self):
        response = self.client.get(reverse('games'))
        self.assertTemplateUsed(response, 'grunt/games.html')

    def test_games_show_up_on_home_page(self):
        """ Games should be listed on the home page """
        expected_games = mommy.make(Game, _quantity = 10)
        response = self.client.get(reverse('games'))
        visible_games = response.context['game_list']
        self.assertListEqual(expected_games, list(visible_games))

    def test_inactive_games_not_shown(self):
        """ Games can be active or inactive """
        inactive_games = mommy.make(Game, status = "INACT", _quantity = 10)
        response = self.client.get(reverse('games'))
        self.assertEqual(len(response.context['game_list']), 0)


class NewGameViewTest(ViewTest):
    def test_new_game_page_renders_new_game_form(self):
        """ Simple, standalone page to make a new game """
        new_game_page_url = reverse('new_game')
        response = self.client.get(new_game_page_url)
        form_in_response = response.context['form']
        self.assertIsInstance(form_in_response, NewGameForm)


class PlayViewTest(ViewTest):
    def setUp(self):
        super(PlayViewTest, self).setUp()
        self.game = mommy.make(Game)
        self.chain = mommy.make(Chain, game = self.game)
        self.message = mommy.make(Message, chain = self.chain)

    def post_response(self):
        with open(self.audio_path, 'rb') as audio_handle:
            audio_file = File(audio_handle)
            post_url = self.game.get_absolute_url()
            post_data = {'parent': self.message.pk, 'audio': audio_file}
            response = self.client.post(post_url, post_data)
        return response

    def test_instructions_page(self):
        """ First visit should render instructions template """
        response = self.client.get(self.game.get_absolute_url())
        self.assertTemplateUsed(response, 'grunt/instruct.html')

    def test_response_form(self):
        """ Should return a ResponseForm """
        self.make_session(self.game, instructed = True)
        response = self.client.get(self.game.get_absolute_url())
        self.assertIsInstance(response.context['form'], ResponseForm)

    def test_initial_form_data(self):
        """ EntryForms should be attached to a next entry instance """
        self.make_session(self.game, instructed = True)
        response = self.client.get(self.game.get_absolute_url())

        initial = response.context['form'].initial
        self.assertEquals(initial['parent'], self.message.pk)

    def test_post_a_message(self):
        """ Post a message """
        messages_before_post = Message.objects.count()
        self.post_response()
        self.assertEquals(Message.objects.count(), messages_before_post + 1)

    def test_post_adds_receipt_to_session(self):
        """ Posting an entry adds a receipt to the session """
        self.post_response()
        self.assertIn(self.chain.pk, self.client.session['receipts'])

    def test_post_redirects_to_complete(self):
        """ Posting an entry should redirect to the completion page """
        self.make_session(self.game, instructed = True)
        response = self.post_response()
        self.assertTemplateUsed(response, 'grunt/complete.html')

    def test_invalid_post(self):
        """ Post an entry without a recording """
        invalid_post = {'parent': self.message.pk}
        response = self.client.post(self.game.get_absolute_url(), invalid_post)
        errors = response.context['form'].non_field_errors()
        self.assertEquals(errors[0], "No audio file found")

    def test_exclude_chains_in_session(self):
        """ If there are receipts in the session, get the correct chain """
        second_chain = mommy.make(Chain, game = self.game)
        mommy.make(Message, chain = second_chain)

        self.make_session(self.game, instructed = True,
                receipts = [self.chain.pk, ])

        response = self.client.get(self.game.get_absolute_url())

        initial_message_parent_pk = response.context['form'].initial['parent']
        initial_message_parent = Message.objects.get(pk = initial_message_parent_pk)
        selected_chain_pk = initial_message_parent.pk
        self.assertEquals(selected_chain_pk, second_chain.pk)

    def test_post_leads_to_next_cluster(self):
        """ Posting a message should redirect to another message """
        second_chain = mommy.make(Chain, game = self.game)
        mommy.make(Message, chain = second_chain)

        self.make_session(self.game, instructed = True)

        response = self.post_response()
        self.assertIsInstance(response.context['form'], ResponseForm)

class InspectViewTest(ViewTest):

    def test_game_inspect_url(self):
        """ Games should return a url for viewing the clusters """
        game = mommy.make(Game)
        expected_url = '/games/1/inspect/'
        self.assertEquals(expected_url, game.get_inspect_url())

    def test_inspect_template(self):
        """ Inspecting a game uses the inspect.html template """
        game = mommy.make(Game)
        response = self.client.get(game.get_inspect_url())
        self.assertTemplateUsed(response, 'grunt/inspect.html')

class UploadMessageViewTest(ViewTest):

    def test_uploading_audio_to_empty_message_fills_that_message(self):
        empty_message = mommy.make(Message)

        self.assertEquals(empty_message.audio, '')

        url = reverse('upload', kwargs = {'pk': empty_message.pk})
        with open(self.audio_path, 'rb') as audio_handle:
            self.client.post(url, {'audio': audio_handle})

        seed_message = Message.objects.get(pk = empty_message.pk)
        self.assertNotEqual(seed_message.audio, '')

    def test_uploading_audio_to_empty_message_sprouts_new_message(self):
        chain = mommy.make(Chain)
        seed_message = mommy.make(Message, chain = chain)
        url = reverse('upload', kwargs = {'pk': seed_message.pk})
        with open(self.audio_path, 'rb') as audio_handle:
            self.client.post(url, {'audio': audio_handle})

        messages_in_chain = chain.message_set.all()
        self.assertEquals(len(messages_in_chain), 2)

        last_message = chain.message_set.last()
        self.assertEquals(last_message.parent, seed_message)

class CloseViewTest(ViewTest):

    def test_close_message_chain(self):
        chain = mommy.make(Chain)
        seed = mommy.make(Message, chain = chain)
        child = mommy.make(Message, parent = seed, chain = chain)

        seed_children = seed.message_set.all()
        self.assertEquals(len(seed_children), 1)

        url = reverse('close', kwargs = {'pk': child.pk})
        self.client.post(url)

        chain_messages = chain.message_set.all()
        self.assertEquals(len(chain_messages), 1)

        seed_children = seed.message_set.all()
        self.assertEquals(len(seed_children), 0)
