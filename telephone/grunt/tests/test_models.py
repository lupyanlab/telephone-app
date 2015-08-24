
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.models import Game, Chain, Message

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

    def test_chain_order(self):
        """ Games can be sequential or random """
        for opt in ['SEQ', 'RND']:
            mommy.make(Game, chain_order = opt)

    def test_chain_order_default(self):
        """ Games select clusters in order by default """
        game = mommy.make(Game)
        self.assertEquals(game.chain_order, 'SEQ')

    def test_status(self):
        """ Games are active or inactive """
        for opt in ['ACTIV', 'INACT']:
            mommy.make(Game, status = opt)

    def test_status_default(self):
        """ Games are active by default """
        game = mommy.make(Game)
        self.assertEquals(game.status, 'ACTIV')

    def test_str(self):
        """ Games can be provided a name """
        game = mommy.make(Game, name = 'The Game Name')
        self.assertEquals(str(game), 'The Game Name')

    def test_str_default(self):
        """ By default games are named based on their primary key """
        game = mommy.make(Game)
        self.assertEquals(str(game), 'game-{}'.format(game.pk))

    def test_dirname(self):
        """ Games are stored in separate directories """
        game = mommy.make(Game)
        self.assertEquals(game.dirname(), 'game-{pk}'.format(pk = game.pk))

    def test_dirname_ignores_name(self):
        """ Game directories are not named by the game name """
        game = mommy.make(Game, name = 'The Game Name')
        self.assertEquals(game.dirname(), 'game-{pk}'.format(pk = game.pk))

    def test_pick_next_chain_sequential(self):
        """ Games can pick the next chain, excluding based on receipts """
        game = mommy.make(Game)
        chains = mommy.make(Chain, game = game, _quantity = 2)
        receipts = [chain.pk for chain in chains]
        self.assertEquals(game.pick_next_chain(), chains[0])
        self.assertEquals(game.pick_next_chain(receipts[:1]), chains[1])

    def test_pick_next_chain_fails_when_game_is_empty(self):
        """ Raise a DoesNotExist exception when picking from an empty game """
        game = mommy.make(Game)
        with self.assertRaises(Chain.DoesNotExist):
            game.pick_next_chain()

    def test_pick_next_chain_fails_when_all_chains_excluded(self):
        """ Raise a DoesNotExist exception when all chains have been picked """
        game = mommy.make(Game)
        chain = mommy.make(Chain, game = game)
        with self.assertRaises(Chain.DoesNotExist):
            game.pick_next_chain(receipts = [chain.pk, ])


class ChainTest(ModelTest):
    def setUp(self):
        super(ChainTest, self).setUp()
        self.game = mommy.make(Game)

    def test_make_a_chain(self):
        """ Chains need to be assigned to a game """
        chain = Chain(game = self.game)
        chain.full_clean()
        chain.save()

    def test_selection_method(self):
        """ Chains can select messages in different ways """
        for opt in ['YNG', 'RND']:
            mommy.make(Chain, selection_method = opt)

    def test_selection_method_default(self):
        """ Chains select messages with the smallest generation by default """
        chain = mommy.make(Chain)
        self.assertEquals(chain.selection_method, 'YNG')

    def test_select_empty_message(self):
        """ Chains pick the next message out of related messages """
        chain = mommy.make(Chain)
        message = mommy.make(Message, chain = chain)
        self.assertEquals(chain.select_empty_message(), message)

    def test_select_empty_message_youngest(self):
        """ Chains pick youngest messages based on the generation """
        chain = mommy.make(Chain, selection_method = 'YNG')
        old_message = mommy.make(Message, generation = 5, chain = chain)
        young_message = mommy.make(Message, generation = 4, chain = chain)
        self.assertEquals(chain.select_empty_message(), young_message)

    def test_pick_only_empty_messages(self):
        """ Chains only select messages that don't already have audio """
        chain = mommy.make(Chain)
        message = mommy.make(Message, chain = chain,
                             _fill_optional = ['audio', ])
        with self.assertRaises(Message.DoesNotExist):
            chain.select_empty_message()

    def test_nesting_calculates_tree_size(self):
        chain = mommy.make(Chain)
        seed = mommy.make(Message, chain = chain, generation = 0,
                          _fill_optional = ['audio', ])
        mommy.make(Message, chain = chain, parent = seed, generation = 1,
                   _fill_optional = ['audio'], _quantity = 2)
        nested = chain.nest()

        self.assertIn('generations', nested.keys())
        self.assertEquals(nested['generations'], 2)

        self.assertIn('branches', nested.keys())
        self.assertEquals(nested['branches'], 2)


class MessageTest(ModelTest):
    def setUp(self):
        super(MessageTest, self).setUp()
        self.chain = mommy.make(Chain)

        # test file for models.FileField
        fpath = Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')
        self.audio = File(open(fpath, 'rb'))

    def test_make_a_message(self):
        """ Messages need to be assigned to a chain """
        message = Message(chain = self.chain)
        message.full_clean()
        message.save()

    def test_replicate(self):
        message = mommy.make(Message)
        child = message.replicate()
        children = message.message_set.all()
        self.assertIn(child, children, 'Child not linked to parent')

    def test_replicate_generation(self):
        message = mommy.make(Message)
        child = message.replicate()
        self.assertEquals(child.generation, message.generation + 1)

    def test_str(self):
        message = mommy.make(Message, name = 'new-message')
        self.assertEquals(str(message), 'new-message')

    def test_str_default(self):
        message = mommy.make(Message)
        self.assertEquals(str(message), 'message-1')
