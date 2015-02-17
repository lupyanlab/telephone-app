
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from unipath import Path
from model_mommy import mommy

from telephone.forms import EntryForm
from telephone.models import Game, Seed, Cluster, Chain, Entry

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class ViewTests(TestCase):

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()

    @property
    def _wav(self):
        # something that can be passed in the wav_file field of Entry objects
        sound = Path(settings.APP_DIR, 'telephone/tests/media/test-audio.wav')
        return File(open(sound, 'r'))

    def make_session(self, game, instructed = False, receipts = []):
        self.client.get(game.get_absolute_url())
        session = self.client.session
        session['receipts'] = receipts
        session['instructed'] = instructed
        session.save()

class GameListTests(ViewTests):

    def test_home_page_renders_game_list_template(self):
        """ Make sure the home page is linked up to the list template """
        response = self.client.get('/calls/')
        self.assertTemplateUsed(response, 'telephone/list.html')

    def test_games_show_up_on_home_page(self):
        """ Games should be listed on the home page """
        expected_games = mommy.make(Game, _quantity = 10)
        response = self.client.get('/calls/')
        visible_games = response.context['game_list']
        self.assertListEqual(expected_games, list(visible_games))

class PlayGameViewTests(ViewTests):

    def create_game(self, returning = ['game', ]):
        objs = {}
        objs['game'] = mommy.make(Game)
        objs['cluster'] = mommy.make(Cluster, game = objs['game'])
        objs['chain'] = mommy.make(Chain, cluster = objs['cluster'])
        objs['entry'] = mommy.make(Entry, chain = objs['chain'])
        return (objs[x] for x in returning)

    def create_post(self, chain):
        entry = chain.prepare_entry()
        return {'chain': entry.chain.pk,
                'parent': entry.parent.pk,
                'content': self._wav}

    def test_instructions_page(self):
        """ First visit should render instructions template """
        game = mommy.make(Game)
        response = self.client.get(game.get_absolute_url())
        self.assertTemplateUsed(response, 'telephone/instruct.html')

    def test_entry_form(self):
        """ Should return an EntryForm """
        (game, ) = self.create_game()
        self.make_session(game, instructed = True)
        response = self.client.get(game.get_absolute_url())
        self.assertIsInstance(response.context['form'], EntryForm)

    def test_initial_form_data(self):
        """ EntryForms should be attached to a next entry instance """
        (game, chain, entry) = self.create_game(
            returning = ['game', 'chain', 'entry'])

        self.make_session(game, instructed = True)
        response = self.client.get(game.get_absolute_url())

        initial = response.context['form'].initial
        self.assertEquals(initial['chain'], chain.pk)
        self.assertEquals(initial['parent'], entry.pk)

    def test_post_an_entry(self):
        """ Post an entry """
        (game, chain) = self.create_game(returning = ['game', 'chain'])
        self.make_session(game, instructed = True)

        post = self.create_post(chain)
        entries_before_post = Entry.objects.count()
        self.client.post(game.get_absolute_url(), post)
        self.assertEquals(Entry.objects.count(), entries_before_post + 1)

    def test_post_adds_receipt_to_session(self):
        """ Posting an entry adds a receipt to the session """
        (game, cluster, chain) = self.create_game(
            returning = ['game', 'cluster', 'chain'])
        self.make_session(game, instructed = True)

        post = self.create_post(chain)
        response = self.client.post(game.get_absolute_url(), post)

        self.assertIn(cluster.pk, self.client.session['receipts'])

    def test_post_redirects_to_complete(self):
        """ Posting an entry should redirect to the completion page """
        (game, cluster, chain) = self.create_game(
            returning = ['game', 'cluster', 'chain'])
        self.make_session(game, instructed = True, receipts = [cluster.pk, ])

        post = self.create_post(chain)
        response = self.client.post(game.get_absolute_url(), post)

        self.assertTemplateUsed(response, 'telephone/complete.html')

    def test_invalid_post(self):
        """ Post an entry without a recording """
        (game, chain, entry) = self.create_game(
            returning = ['game', 'chain', 'entry']
        )

        self.make_session(game, instructed = True)

        invalid_post = {'chain': chain.pk, 'parent': entry.pk}
        response = self.client.post(game.get_absolute_url(), invalid_post)
        errors = response.context['form'].errors
        self.assertEquals(errors['content'][0], "You didn't make a recording")

    def test_exclude_clusters_in_session(self):
        """ If there are receipts in the session, get the correct cluster """
        (game, cluster_1) = self.create_game(returning = ['game', 'cluster'])
        cluster_2 = mommy.make(Cluster, game = game)

        self.make_session(game, instructed = True, receipts = [cluster_2.pk, ])

        response = self.client.get(game.get_absolute_url())

        initial = response.context['form'].initial
        initial_cluster = Chain.objects.get(pk = initial['chain']).cluster

        self.assertEquals(initial_cluster, cluster_1)

    def test_post_leads_to_next_cluster(self):
        """ Posting an entry should return a new form """
        (game, ) = self.create_game()
        cluster = mommy.make(Cluster, game = game)
        chain = mommy.make(Chain, cluster = cluster)
        entry = mommy.make(Entry, chain = chain)

        self.make_session(game, instructed = True)

        post = self.create_post(chain)
        response = self.client.post(game.get_absolute_url(), post)
        self.assertIsInstance(response.context['form'], EntryForm)
