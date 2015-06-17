
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.forms import NewGameForm, UpdateMessageForm, ResponseForm
from grunt.models import Game, Chain, Message

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class FormTest(TestCase):
    def setUp(self):
        super(FormTest, self).setUp()
        self.audio_path = Path(
            settings.APP_DIR,
            'grunt/tests/media/test-audio.wav')

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()


class NewGameFormTest(FormTest):
    def test_make_a_valid_game(self):
        """ Simulate making a new game in the browser """
        form = NewGameForm({'name': 'Valid Game Name', 'num_chains': 1})
        self.assertTrue(form.is_valid())

    def test_valid_form_saves_new_game(self):
        """ Ensure that saving a form creates a new game """
        new_game_name = 'My Real Game'
        form = NewGameForm({'name': new_game_name, 'num_chains': 1})
        form.save()
        last_saved_game = Game.objects.last()
        self.assertEquals(last_saved_game.name, new_game_name)

    def test_new_game_form_saves_with_chain(self):
        """ Ensure that new games are populated with a chain """
        form = NewGameForm({'name': 'New Game', 'num_chains': 1})
        game = form.save()
        self.assertEquals(game.chain_set.count(), 1)

    def test_new_game_form_saves_with_multiple_chains(self):
        """ Should be able to make new games with multiple chains """
        form = NewGameForm({'name': 'Two Chain Game', 'num_chains': 2})
        game = form.save()
        self.assertEquals(game.chain_set.count(), 2)

class ResponseFormTest(FormTest):
    def setUp(self):
        super(ResponseFormTest, self).setUp()
        self.empty_message = mommy.make(Message)

    def submit_form(self, message_pk):
        saved_message = None
        with open(self.audio_path, 'rb') as audio_handle:
            audio_file = File(audio_handle)
            form = ResponseForm({'message': message_pk},
                                files = {'audio': audio_file})
            saved_message = form.save()
        return saved_message

    def test_use_response_form_to_update_an_empty_message(self):
        """ Simulate making an message from a POST """
        updated_message = None

        with open(self.audio_path, 'rb') as audio_handle:
            audio_file = File(audio_handle)
            form = ResponseForm({'message': self.empty_message.pk},
                                files = {'audio': audio_file})
            updated_message = form.save()
        self.assertEquals(updated_message.pk, self.empty_message.pk)
        self.assertEquals(updated_message.chain, self.empty_message.chain)

    def test_updating_an_empty_message_sprouts_new_empty_message(self):
        updated_message = None

        with open(self.audio_path, 'rb') as audio_handle:
            audio_file = File(audio_handle)
            form = ResponseForm({'message': self.empty_message.pk},
                                files = {'audio': audio_file})
            updated_message = form.save()

        # sprouts a single child
        child_messages = updated_message.message_set.all()
        self.assertEquals(len(child_messages), 1)

        # the sprouted child has no audio
        empty_child_message = child_messages[0]
        self.assertEquals(empty_child_message.audio, '')

        # the sprouted child has the same chain as the parent
        self.assertEquals(empty_child_message.chain, updated_message.chain)

    def test_provide_response_form_message_pk_to_update_existing(self):
        updated_message = None

        with open(self.audio_path, 'rb') as audio_handle:
            audio_file = File(audio_handle)
            form = ResponseForm({'message': self.empty_message.pk},
                                files = {'audio': audio_file})
            self.assertTrue(form.is_valid())
            updated_message = form.save()

        self.assertEquals(updated_message.pk, self.empty_message.pk)
        self.assertEquals(updated_message.chain, self.empty_message.chain)

    def test_response_form_without_audio_is_invalid(self):
        form = ResponseForm({'message': self.empty_message.pk})
        self.assertFalse(form.is_valid())

    def test_two_responses_to_the_same_message(self):
        chain = mommy.make(Chain)
        seed_message = mommy.make(Message, chain = chain,
                                  _fill_optional = ['audio', ])
        empty_message = mommy.make(Message, chain = chain, parent = seed_message)

        first_message = self.submit_form(empty_message.pk)
        self.assertEquals(empty_message.pk, first_message.pk)
        self.assertNotEqual(first_message.audio, '')
        self.assertEquals(chain.message_set.count(), 3)

        filled_messages = chain.message_set.exclude(audio = '')
        self.assertEquals(len(filled_messages), 2)

        second_message = self.submit_form(empty_message.pk)
        self.assertNotEqual(empty_message.pk, second_message.pk)
        self.assertNotEqual(second_message.audio, '')

        messages = chain.message_set.all()
        self.assertEquals(len(messages), 5)

        filled_messages = messages.exclude(audio = '')
        self.assertEquals(len(filled_messages), 3)

class UpdateMessageFormTest(FormTest):
    def setUp(self):
        super(UpdateMessageFormTest, self).setUp()
        self.empty_message = mommy.make(Message)

    def test_upload_audio_to_empty_message(self):
        self.assertEqual(self.empty_message.audio, '')

        updated_message = None

        with open(self.audio_path, 'rb') as audio_handle:
            audio_file = File(audio_handle)
            form = UpdateMessageForm(instance = self.empty_message,
                                     files = {'audio': audio_file})
            self.assertTrue(form.is_valid())

            updated_message = form.save()

        self.assertNotEqual(updated_message.audio, '')
