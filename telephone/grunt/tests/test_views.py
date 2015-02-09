
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from unipath import Path
from model_mommy import mommy

from grunt.forms import EntryForm
from grunt.models import Game, Seed, Cluster, Chain, Entry

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class ViewTests(TestCase):

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()

    @property
    def _wav(self):
        # something that can be passed in the wav_file field of Entry objects
        sound = Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')
        return File(open(sound, 'r'))

class GameListTests(ViewTests):

    def test_home_page_renders_game_list_template(self):
        """ Make sure the home page is linked up to the list template """
        response = self.client.get('/grunt/')
        self.assertTemplateUsed(response, 'grunt/list.html')

    def test_games_show_up_on_home_page(self):
        """ Games should be listed on the home page """
        expected_games = mommy.make(Game, _quantity = 10)
        response = self.client.get('/grunt/')
        visible_games = response.context['game_list']
        self.assertListEqual(expected_games, list(visible_games))

class SingleClusterTests(ViewTests):

    def setUp(self):
        super(SingleClusterTests, self).setUp()
        self.game = mommy.make(Game)
        self.game_url = self.game.get_absolute_url()

        self.cluster = mommy.make(Cluster, game = self.game)
        self.chain = mommy.make(Chain, cluster = self.cluster)
        self.entry = mommy.make(Entry, chain = self.chain)

    def get_post_data(self):
        entry = self.chain.prepare_entry()
        return {'chain': entry.chain.pk,
                'parent': entry.parent.pk,
                'content': self._wav}

    def test_context_data(self):
        """ Should return an EntryForm """
        response = self.client.get(self.game_url)
        self.assertIsInstance(response.context['form'], EntryForm)

    def test_initial_form_data(self):
        """ EntryForms should be attached to a next entry instance """
        response = self.client.get(self.game_url)
        initial = response.context['form'].initial
        self.assertEquals(initial['parent'], self.entry.pk)
        self.assertEquals(initial['chain'], self.chain.pk)

        form = EntryForm(data = initial, files = {'content': self._wav})
        self.assertTrue(form.is_valid())

    def test_session_receipts(self):
        """ Arriving at a game page should initialize a list of receipts """
        self.client.get(self.game_url)
        self.assertEquals(self.client.session['receipts'], list())

    def test_post_entry(self):
        """ Post an entry """
        entries_before_post = Entry.objects.count()
        self.client.post(self.game_url, self.get_post_data())
        self.assertEquals(Entry.objects.count(), entries_before_post + 1)


    def test_post_adds_receipt_to_session(self):
        """ Posting an entry redirects when there are no other clusters """
        response = self.client.post(self.game_url, self.get_post_data())
        self.assertIn(self.cluster.pk, self.client.session['receipts'])

    def test_post_without_content(self):
        """ Posting an entry without making a recording should error """
        entry = self.chain.prepare_entry()
        invalid_post_data = {
            'chain': entry.chain.pk,
            'parent': entry.parent.pk
        }
        response = self.client.post(self.game_url, invalid_post_data)
        errors = response.context['form'].errors
        self.assertEquals(errors['content'][0], "You didn't make a recording")

class MultiClusterTests(ViewTests):

    def setUp(self):
        super(MultiClusterTests, self).setUp()
        self.game = mommy.make(Game)
        self.game_url = self.game.get_absolute_url()

        self.clusters = mommy.make(Cluster, game = self.game, _quantity = 2)
        for cluster in self.clusters:
            tmp_chain = mommy.make(Chain, cluster = cluster)
            mommy.make(Entry, chain = tmp_chain)

    def get_post_data(self, chain = None, cluster = None):
        """ Helper function for generate the data for a post

        Option parameters allow specifying the entry chain or cluster from
        within the test call.
        """
        if not chain:
            cluster = cluster or self.game.pick_cluster()
            chain = cluster.pick_chain()

        entry = chain.prepare_entry()
        return {'chain': entry.chain.pk,
                'parent': entry.parent.pk,
                'content': self._wav}

class MultiClusterGetTests(MultiClusterTests):

    def conjure_session(self, receipts = []):
        self.client.get(self.game_url)
        session = self.client.session
        session['receipts'] = receipts
        session.save()

    def test_get_with_receipts(self):
        """ If there are receipts in the session, get the correct cluster """
        receipt = self.clusters[0].pk
        self.conjure_session(receipts = [receipt, ])

        response = self.client.get(self.game_url)

        initial = response.context['form'].initial
        initial_cluster = Chain.objects.get(pk = initial['chain']).cluster

        self.assertEquals(initial_cluster, self.clusters[1])

class MultiCusterPostTests(MultiClusterTests):

    def test_post_new_entry_to_db_with_multiple_clusters(self):
        """ Posting an entry should be the same with multiple clusters """
        entries_before_post = Entry.objects.count()
        chain = self.game.pick_cluster().pick_chain()
        data = self.get_post_data(chain = chain)
        self.client.post(self.game_url, data)
        self.assertEquals(Entry.objects.count(), entries_before_post + 1)

        last_saved_entry = chain.entry_set.last()
        self.assertEquals(last_saved_entry.chain.pk, data['chain'])
        self.assertEquals(last_saved_entry.parent.pk, data['parent'])

    def test_post_leads_to_next_cluster(self):
        """ Posting an entry should return a new form """
        data = self.get_post_data()
        response = self.client.post(self.game_url, data)
        self.assertIsInstance(response.context['form'], EntryForm)

    def test_post_adds_receipt_to_session(self):
        """ Posting an entry should add the cluster receipt to the session """
        cluster = self.game.pick_cluster()
        data = self.get_post_data(cluster = cluster)
        response = self.client.post(self.game_url, data)
        self.assertIn(cluster.pk, self.client.session['receipts'])


class ConfirmationPageTests(ViewTests):

    def test_confirmation_page_puts_game_in_context(self):
        """ The confirmation page should fetch the game and render it """
        game = mommy.make(Game)
        response = self.client.get('/grunt/{}/complete/'.format(game.pk))
        self.assertEquals(response.context['game'], game)
