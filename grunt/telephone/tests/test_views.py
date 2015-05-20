
from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from unipath import Path
from model_mommy import mommy

from telephone.forms import ResponseForm, MessageForm
from telephone.models import Game, Chain, Message

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class ViewTest(TestCase):
    def setUp(self):
        fpath = Path(settings.APP_DIR, 'telephone/tests/media/test-audio.wav')
        self.audio = File(open(fpath, 'rb'))

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
        self.assertTemplateUsed(response, 'telephone/games.html')

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


class PlayViewTest(ViewTest):
    def setUp(self):
        super(PlayViewTest, self).setUp()
        self.game = mommy.make(Game)
        self.chain = mommy.make(Chain, game = self.game)
        self.message = mommy.make(Message, chain = self.chain,
                audio = self.audio)

    def test_instructions_page(self):
        """ First visit should render instructions template """
        response = self.client.get(self.game.get_absolute_url())
        self.assertTemplateUsed(response, 'telephone/instruct.html')

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
        post = {
            'chain': self.chain.pk,
            'parent': self.message.pk,
            'audio': self.audio
        }
        messages_before_post = Message.objects.count()
        self.client.post(self.game.get_absolute_url(), post)
        self.assertEquals(Message.objects.count(), messages_before_post + 1)

    def test_post_adds_receipt_to_session(self):
        """ Posting an entry adds a receipt to the session """
        post = {
            'chain': self.chain.pk,
            'parent': self.message.pk,
            'audio': self.audio
        }
        response = self.client.post(self.game.get_absolute_url(), post)
        self.assertIn(self.chain.pk, self.client.session['receipts'])

    def test_post_redirects_to_complete(self):
        """ Posting an entry should redirect to the completion page """
        post = {
            'parent': self.message.pk,
            'audio': self.audio
        }
        response = self.client.post(self.game.get_absolute_url(), post)
        self.assertTemplateUsed(response, 'telephone/complete.html')

    def test_invalid_post(self):
        """ Post an entry without a recording """
        invalid_post = {'chain': self.chain.pk, 'parent': self.message.pk}
        response = self.client.post(self.game.get_absolute_url(), invalid_post)
        errors = response.context['form'].errors
        self.assertEquals(errors['content'][0], "You didn't make a recording")

    def test_exclude_chains_in_session(self):
        """ If there are receipts in the session, get the correct chain """
        second_chain = mommy.make(Chain, game = self.game)
        self.make_session(self.game, instructed = True,
                receipts = [self.chain.pk, ])

        response = self.client.get(self.game.get_absolute_url())

        selected_chain_pk = response.context['form'].initial['chain']
        self.assertEquals(selected_chain_pk, second_chain.pk)

    def test_post_leads_to_next_cluster(self):
        """ Posting a message should redirect to another message """
        second_chain = mommy.make(Chain, game = self.game)
        second_message = mommy.make(Message, chain = second_chain,
            audio = self.audio)

        self.make_session(self.game, instructed = True)
        post = {
            'chain': self.chain.pk,
            'parent': self.message.pk,
            'audio': self.audio
        }
        response = self.client.post(self.game.get_absolute_url(), post)
        self.assertIsInstance(response.context['form'], ResponseForm)

    def test_revisit_game(self):
        """ Getting the game page after submitting should bring up dialog """
        self.make_session(self.game, instructed = True,
                receipts = [self.chain.pk, ])

        response = self.client.get(self.game.get_absolute_url())
        self.assertTemplateUsed(response, 'telephone/complete.html')


class MessageViewTest(ViewTest):
    def test_message_view_returns_correct_form(self):
        chain = mommy.make(Chain)
        message = mommy.make(Message, chain = chain)
        response = self.client.get(message.get_absolute_url())
        self.assertIsInstance(response.context['form'], MessageForm)

    def test_message_view_url(self):
        chain = mommy.make(Chain)
        message = mommy.make(Message, chain = chain)
        expected_url = '/games/1/{}/{}/'.format(chain, message.pk)
        self.assertEquals(expected_url, message.get_absolute_url())


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
        self.assertTemplateUsed(response, 'telephone/inspect.html')
