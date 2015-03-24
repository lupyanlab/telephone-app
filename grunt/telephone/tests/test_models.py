
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import IntegrityError
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from telephone.models import Game, Call, Message, Seed, Cluster, Chain, Entry

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class ModelTest(TestCase):
    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()


class GameTest(ModelTest):
    def test_make_a_game(self):
        """ Make a game """
        game = Game()
        game.full_clean()
        game.save()

    def test_num_calls(self):
        """ Games start with a number of calls """
        game = mommy.make(Game, num_calls = 10)
        self.assertEquals(game.call_set.count(), 10)

    def test_num_calls_default(self):
        """ Games start with a single call by default """
        game = mommy.make(Game)
        self.assertEquals(game.call_set.count(), 1)

    def test_num_calls_none(self):
        """ Creating a call on save can be prevented """
        game = mommy.make(Game, num_calls = 0)
        self.assertEquals(game.call_set.count(), 0)

    def test_call_order(self):
        """ Games can be sequential or random """
        for opt in ['SEQ', 'RND']:
            mommy.make(Game, call_order = opt)

    def test_call_order_default(self):
        """ Games select clusters in order by default """
        game = mommy.make(Game)
        self.assertEquals(game.call_order, 'SEQ')

    def test_status(self):
        """ Games are active or inactive """
        for opt in ['ACTIV', 'INACT']:
            mommy.make(Game, status = opt)

    def test_status_default(self):
        """ Games are active by default """
        game = mommy.make(Game)
        self.assertEquals(game.status, 'ACTIV')

    def test_str_default(self):
        """ By default games are named based on their primary key """
        game = mommy.make(Game)
        self.assertEquals(str(game), 'game-{}'.format(game.pk))

        # but human-readable names can be provided
        game = mommy.make(Game, name = 'The Game Name')
        self.assertEquals(str(game), 'The Game Name')

    def test_dirname(self):
        game = mommy.make(Game)
        self.assertEquals(game.dirname(), 'game-{pk}'.format(pk = game.pk))

        # still use the unique pk even when a name is provided
        game = mommy.make(Game, name = 'the game name')
        self.assertEquals(game.dirname(), 'game-{pk}'.format(pk = game.pk))

    def test_pick_next_call_sequential(self):
        """ Games can pick the next call, excluding based on receipts """
        game = mommy.make(Game, num_calls = 0)
        calls = mommy.make(Call, game = game, _quantity = 2)
        receipts = [call.pk for call in calls]
        self.assertEquals(game.pick_next_call(), calls[0])
        self.assertEquals(game.pick_next_call(receipts=receipts[:1]), calls[1])

    # I don't know a good way to test this
    # def test_pick_next_call_random(self):
    #     pass

    def test_pick_next_call_fails_when_game_is_empty(self):
        game = mommy.make(Game, num_calls = 0)
        with self.assertRaises(Call.DoesNotExist):
            game.pick_next_call()

    def test_pick_next_call_fails_when_all_calls_excluded(self):
        game = mommy.make(Game, num_calls = 0)
        call = mommy.make(Call, game = game)
        with self.assertRaises(Call.DoesNotExist):
            game.pick_next_call(receipts = [call.pk, ])

    # def test_mturk_games_require_a_completion_code(self):
    #     with self.assertRaises(ValidationError):
    #         mommy.make(Game, type = 'MTK', completion_code = '')

class CallTest(ModelTest):
    def setUp(self):
        super(CallTest, self).setUp()
        self.game = mommy.make(Game)

    def test_make_a_call(self):
        """ Calls need to be assigned to a game """
        call = Call(game = self.game)
        call.full_clean()
        call.save()

    def test_num_seeds(self):
        """ Calls start with a number of seed messages """
        call = mommy.make(Call, num_seeds = 10)
        self.assertEquals(call.message_set.count(), 10)

    def test_num_seeds_default(self):
        """ Calls start with a single seed message by default """
        call = mommy.make(Call)
        self.assertEquals(call.message_set.count(), 1)

    def test_num_seeds_none(self):
        """ Calls can be created without any seed messages """
        call = mommy.make(Call, num_seeds = 0)
        self.assertEquals(call.message_set.count(), 0)

    def test_num_seeds_edit(self):
        """ Calls can be edited to create more seed messages """
        call = mommy.make(Call)
        call.num_seeds = 10
        call.save()
        self.assertEquals(call.message_set.count(), 10)

    def test_num_seeds_remove_error(self):
        """ Seeds cannot be removed by editing a call """
        call = mommy.make(Call)
        call.num_seeds = 0
        with self.assertRaises(ValidationError):
            call.save()

class MessageTest(ModelTest):
    def setUp(self):
        super(MessageTest, self).setUp()
        fpath = Path(settings.APP_DIR, 'telephone/tests/media/test-audio.wav')
        self.content = File(open(fpath, 'rb'))

class SeedMessageTest(MessageTest):
    def test_make_a_seed_message(self):
        seed = Message(type = 'SEED', name = 'test-seed', audio = self.content)
        seed.full_clean()
        seed.save()

    def test_seeds_are_saved_to_seed_dir(self):
        seed = mommy.make(Message, type = 'SEED',
                name = 'test-seed', audio = self.content)
        self.assertEquals(seed.audio.url, '/media/seeds/test-seed.wav')

class ResponseMessageTest(MessageTest):
    def setUp(self):
        super(ResponseMessageTest, self).setUp()
        self.call = mommy.make(Call)
        self.seed = mommy.make(Message, type = 'SEED', name = 'test-seed')

    def test_make_a_response_message(self):
        response = Message(type = 'RESP', call = self.call, parent = self.seed,
                audio = self.content)
        response.full_clean()
        response.save()

    def test_responses_are_saved_to_call_dir(self):
        response = mommy.make(Message, type = 'RESP', call = self.call,
                parent = self.seed, audio = self.content, generation = 1)
        self.assertEquals(response.audio.url,
                '/media/game-1/call-1/gen-1.wav'.format(self.seed.name))

    def test_saving_a_response_creates_a_new_sprout(self):
        response = mommy.make(Message, type = 'RESP', call = self.call)
        sprout = Message.objects.filter(type = 'SPRT').first()
        self.assertEquals(sprout.parent, response)

class SproutMessageTest(MessageTest):
    def setUp(self):
        super(SproutMessageTest, self).setUp()
        self.call = mommy.make(Call)
        self.seed = mommy.make(Message, type = 'SEED', name = 'test-seed')

    def test_make_a_sprout_message(self):
        sprout = Message(type = 'SPRT', call = self.call, parent = self.seed)
        sprout.full_clean()
        sprout.save()

class ChainTest(ModelTest):
    def setUp(self):
        super(ChainTest, self).setUp()
        self.cluster = mommy.make(Cluster)
        self.seed = mommy.make(Seed)

    def test_make_a_chain(self):
        """ Make a chain """
        chain = Chain(cluster = self.cluster, seed = self.seed)
        chain.full_clean()
        chain.save()

    def test_chain_requirements(self):
        """ Validating a chain without a cluster raises an error """
        no_cluster = Chain()
        try:
            no_cluster.full_clean()
        except ValidationError as validation_error:
            errors = validation_error.error_dict
            self.assertListEqual(errors.keys(), ['cluster', 'seed'])

    def test_chain_populates_seed_from_cluster(self):
        seeded_cluster = mommy.make(Cluster, seed = self.seed)
        chain = Chain(cluster = seeded_cluster)
        chain.full_clean()
        self.assertEquals(chain.seed, self.seed)

    def test_chain_str(self):
        """ Chains are named based on their number within the cluster """
        cluster = mommy.make(Cluster)
        chains = mommy.make(Chain, cluster = cluster, _quantity = 3)

        expected = []
        actual = []
        for ix, chain in enumerate(chains):
            expected.append('{}-{}'.format(ix, chain.seed))
            actual.append(str(chain))

        self.assertListEqual(actual, expected)

    def test_chain_directory(self):
        """ Chains know the directory in which to save entries """
        game = mommy.make(Game, name = 'The Game Name')
        cluster = mommy.make(Cluster, game = game)
        chain = Chain.objects.create(cluster = cluster, seed = self.seed)
        expected_dir = '{game}/{cluster}/{chain}/'.format(
            game = game.dir(),
            cluster = cluster.dir(),
            chain = chain.dir()
        )
        self.assertEquals(chain.path(), expected_dir)

    def test_saving_a_chain_populates_first_entry(self):
        """ A side effect of saving a chain is that a seed entry is made """
        chain = Chain(cluster = self.cluster, seed = self.seed)
        chain.full_clean()
        chain.save()
        self.assertEquals(chain.entry_set.count(), 1)

    def test_preparing_next_entry(self):
        """ Chains prepare the next entry using the last entry as parent """
        chain = Chain.objects.create(cluster = self.cluster, seed = self.seed)
        entry = chain.entry_set.first()

        next_entry = chain.prepare_entry()

        self.assertEquals(next_entry.chain.pk, chain.pk)
        self.assertEquals(next_entry.parent.pk, entry.pk)

    def test_create_multiple(self):
        """ ChainManager can make multiple chains at once """
        seeded_cluster = mommy.make(Cluster, seed = self.seed)
        chains = Chain.objects.create_multiple(_quantity = 5, cluster = seeded_cluster)
        self.assertEquals(seeded_cluster.chain_set.count(), 5)
        for chain in seeded_cluster.chain_set.all():
            self.assertEquals(chain.entry_set.count(), 1)

class SeedTest(ModelTest):
    def setUp(self):
        super(SeedTest, self).setUp()
        fpath = Path(settings.APP_DIR, 'telephone/tests/media/test-audio.wav')
        self.content = File(open(fpath, 'rb'))

    def test_make_a_seed(self):
        """ Make a seed """
        seed = Seed(name = 'seed', content = self.content)
        seed.full_clean()
        seed.save()

    def test_seed_requirements(self):
        """ A name w/o a file, or a file w/o a name raises an error """
        valid_name = 'seed'
        valid_content = self.content

        no_name = Seed(content = valid_content)
        with self.assertRaises(ValidationError):
            no_name.full_clean()

        no_content = Seed(name = valid_name)
        with self.assertRaises(ValidationError):
            no_content.full_clean()

        valid = Seed(name = valid_name, content = valid_content)
        valid.full_clean()  # should not raise

    def test_seed_str(self):
        seed = Seed.objects.create(name = 'valid-name', content = self.content)
        self.assertEquals(str(seed), 'valid-name')

    def test_seed_names_are_unique(self):
        """ Seeds can't have the same name """
        repeated = 'repeated-name'

        first = Seed(name = repeated, content = self.content)
        first.full_clean()
        first.save()

        second = Seed(name = repeated, content = self.content)
        with self.assertRaises(ValidationError):
            second.full_clean()

        third = Seed(name = "new-name", content = self.content)
        third.full_clean()  # should not raise
        third.save()

    def test_seeds_are_saved_to_correct_directory(self):
        """ Seeds are saved to their own directory """
        seed = Seed(name = 'seed', content = self.content)
        seed.save()
        self.assertRegexpMatches(seed.content.url, r'/media/seeds/')

    def test_seed_files_are_saved_as_wav(self):
        """ In the telephone app all seeds are .wav files """
        seed = Seed(name = 'seed', content = self.content)
        seed.save()
        seed_content_url = Path(seed.content.url)
        self.assertEquals(seed_content_url.ext, '.wav')


class ClusterTest(ModelTest):
    def setUp(self):
        super(ClusterTest, self).setUp()
        self.game = mommy.make(Game)
        self.seed = mommy.make(Seed)

    def test_make_a_cluster(self):
        """ Make a cluster """
        cluster = Cluster(game = self.game, name = 'first-cluster')
        cluster.full_clean()
        cluster.save()

    def test_cluster_requirements(self):
        """ A game and a name is required for validation """
        empty_cluster = Cluster()
        try:
            empty_cluster.full_clean()
        except ValidationError as validation_error:
            errors = validation_error.error_dict
            self.assertListEqual(errors.keys(), ['game', 'name'])

    def test_make_a_cluster_with_seed(self):
        """ Clusters can be made with a seed """
        cluster = Cluster(game = self.game, seed = self.seed)
        cluster.full_clean()
        self.assertEquals(cluster.name, str(self.seed))

    def test_cluster_defaults(self):
        """ Clusters select the shortest chains by default """
        cluster = Cluster(game = self.game, name = 'my-cluster')
        cluster.full_clean()
        self.assertEquals(cluster.method, 'SRT')

    def test_cluster_str(self):
        """ Clusters are named or get their name from the seed """
        with_name = Cluster.objects.create(
            game = self.game, name = 'cluster-name'
        )
        self.assertEquals(str(with_name), 'cluster-name')

        with_seed = Cluster.objects.create(
            game = self.game, seed = self.seed,
        )
        self.assertEquals(str(with_seed), str(self.seed))

    def test_cluster_generations(self):
        cluster = Cluster.objects.create(game = self.game, seed = self.seed)
        generations = cluster.generations()
        self.assertEquals(len(generations), 1)


class EntryTests(ModelTest):

    def setUp(self):
        super(EntryTests, self).setUp()
        self.chain = mommy.make(Chain)

        fpath = Path(settings.APP_DIR, 'telephone/tests/media/test-audio.wav')
        self.content = File(open(fpath, 'rb'))

    def make_entry(self, save = True):
        entry = Entry(
            content = self.content,
            chain = self.chain,
            parent = self.chain.entry_set.last()
        )
        entry.full_clean()
        if save:
            entry.save()
        return entry

    def test_make_an_entry(self):
        """ Make an entry """
        parent = self.chain.entry_set.last()
        entry = Entry(
            content = self.content,
            chain = self.chain,
            parent = parent
        )
        entry.full_clean()
        entry.save()

    def test_entry_requirements(self):
        """ First generation entries require content and a chain """
        no_chain = Entry(content = self.content)
        with self.assertRaises(ValidationError):
            no_chain.full_clean()

    def test_entries_require_a_parent(self):
        """ Second+ generation entries also require a parent """
        self.assertGreater(self.chain.entry_set.count(), 0)
        entry = Entry(content = self.content, chain = self.chain)
        with self.assertRaises(ValidationError):
            entry.full_clean()

    def test_entry_defaults(self):
        """ Default generation is 0 """
        chain = mommy.make(Chain)
        entry = chain.entry_set.last()
        self.assertEquals(entry.generation, 0)

    def test_generation_is_filled_on_clean(self):
        """ Generation is parent.generation + 1 """
        parent = self.chain.entry_set.last()
        entry = self.make_entry(save = False)
        self.assertEquals(entry.generation, parent.generation + 1)

    def test_entry_str(self):
        """ Entries are named by the seed and the generation """
        expected_name = '{seed}-{generation}'.format(
            seed = str(self.chain.seed),
            generation = 1
        )

        entry = self.make_entry(save = False)
        self.assertEquals(str(entry), expected_name)

    def test_entries_are_saved_to_chain_directory(self):
        """ Entries should be saved in the chain directory """
        entry = self.make_entry(save = True)
        self.assertRegexpMatches(entry.content.url, self.chain.path())

    def test_entry_files_are_saved_as_wav(self):
        """ In the telephone app all entries are .wav files """
        entry = self.make_entry(save = True)

        entry_content_url = Path(entry.content.url)
        self.assertEquals(entry_content_url.ext, '.wav')

    def test_entry_files_are_saved_with_interpretable_names(self):
        """ """
        expected_stem = '{seed}-{generation}'.format(
            seed = str(self.chain.seed),
            generation = 1
        )
        entry = self.make_entry(save = True)
        entry_content_url = Path(entry.content.url)
        self.assertEquals(entry_content_url.stem, expected_stem)

class GameNavigationTests(ModelTest):

    def setUp(self):
        super(GameNavigationTests, self).setUp()
        clusters_per = 5
        chains_per = 10

        # Populate a game with a number of Clusters
        self.game = mommy.make(Game)
        self.clusters = mommy.make(Cluster, game = self.game,
            _quantity = clusters_per)

        for cluster in self.clusters:
            mommy.make(Chain, cluster = cluster, _quantity = chains_per)

        self.visits = [cluster.pk for cluster in self.clusters]


    def test_pick_cluster(self):
        """ Game objects have a method that returns a related cluster """
        cluster = self.game.pick_cluster()
        self.assertIn(cluster, self.clusters)

    def test_pick_cluster_excluding_receipts(self):
        """ When picking the next cluster, exclude based on receipts """
        all_but_one = self.visits[:-1]
        next_cluster = self.game.pick_cluster(all_but_one)
        expected = Cluster.objects.get(pk = self.visits[-1])
        self.assertEquals(next_cluster, expected)

    def test_pick_clusters_in_order(self):
        """ Sequential games pick clusters in the order they were added """
        ordered_game = mommy.make(Game, order = 'SEQ')
        ordered_clusters = mommy.make(Cluster, game=ordered_game, _quantity=20)

        first = ordered_game.pick_cluster()
        second = ordered_game.pick_cluster([first.pk, ])

        self.assertEquals(first, ordered_clusters[0])
        self.assertEquals(second, ordered_clusters[1])

    def test_pick_clusters_at_random(self):
        """ Random games pick clusters at random

        * HACK! *
        """
        random_game = mommy.make(Game, order = 'RND')
        mommy.make(Cluster, game = random_game, _quantity = 20)

        first = random_game.pick_cluster()
        second = random_game.pick_cluster()
        third = random_game.pick_cluster()
        fourth = random_game.pick_cluster()

        self.assertFalse(first == second == third == fourth,
            "Clusters weren't picked at random (could be due to chance!)")

    def test_no_clusters_left(self):
        """ Simulate a user reaching the end of the game """
        with self.assertRaises(Cluster.DoesNotExist):
            self.game.pick_cluster(self.visits)


class ClusterNavigationTests(ModelTest):
    """ When a player reaches a cluster only one chain should be viewed """

    def setUp(self):
        super(ClusterNavigationTests, self).setUp()
        self.cluster = mommy.make(Cluster)
        self.chains = mommy.make(Chain, cluster = self.cluster, _quantity = 20)

    def test_cluster_can_pick_chain(self):
        """ Clusters have a method to select a related chain object """
        next_chain = self.cluster.pick_chain()
        self.assertIn(next_chain, self.chains)

    def test_cluster_can_pick_shortest_chain(self):
        """ By default clusters pick the shortest chain """
        cluster = mommy.make(Cluster, method = 'SRT')
        long_chain = mommy.make(Chain, cluster = cluster)
        mommy.make(Entry, chain = long_chain, _quantity = 2)

        short_chain = mommy.make(Chain, cluster = cluster)
        mommy.make(Entry, chain = short_chain)

        picked = cluster.pick_chain()
        self.assertEquals(picked, short_chain)

    def test_cluster_can_pick_chains_at_random(self):
        """ Clusters pick a chain at random """
        cluster = mommy.make(Cluster, method = 'RND')
        mommy.make(Chain, cluster = cluster, _quantity = 20)

        first = cluster.pick_chain()
        second = cluster.pick_chain()
        third = cluster.pick_chain()
        fourth = cluster.pick_chain()

        self.assertFalse(first == second == third == fourth,
            "Chains weren't picked at random (could be due to chance!)")

    def test_cluster_cant_pick_a_chain_if_none_exist(self):
        """ Edge case: trying to pick a chain without any in the cluster """
        new_cluster = mommy.make(Cluster)
        with self.assertRaises(Chain.DoesNotExist):
            new_cluster.pick_chain()

class GameShortcutTests(ModelTest):

    def test_games_can_prepare_entry(self):
        """ Traverse the game:cluster:chain.prepare_entry """
        game = mommy.make(Game)
        cluster = mommy.make(Cluster, game = game)
        chain = mommy.make(Chain, cluster = cluster)
        entry = mommy.make(Entry, chain = chain)
        prepared_by_game = game.prepare_entry()
        prepared_by_chain = chain.prepare_entry()
        self.assertEquals(prepared_by_game.parent, prepared_by_chain.parent)
        self.assertEquals(prepared_by_game.chain, prepared_by_chain.chain)
