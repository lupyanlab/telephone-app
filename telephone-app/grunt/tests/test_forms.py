
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.forms import NewGameForm, ResponseForm, UploadMessageForm
from grunt.models import Game, Chain, Message

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class FormTest(TestCase):
    def setUp(self):
        fpath = Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')
        self.audio = File(open(fpath, 'rb'))

        self.chain = mommy.make(Chain)
        self.parent_message = mommy.make(Message, chain = self.chain,
                audio = self.audio)

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()


class NewGameFormTest(FormTest):
    def test_make_a_valid_game(self):
        """ Simulate making a new game in the browser """
        form = NewGameForm({'name': 'Valid Game Name'})
        self.assertTrue(form.is_valid())

    def test_valid_form_saves_new_game(self):
        """ Ensure that saving a form creates a new game """
        new_game_name = 'My Real Game'
        form = NewGameForm({'name': new_game_name})
        form.save()
        last_saved_game = Game.objects.last()
        self.assertEquals(last_saved_game.name, new_game_name)

    def test_new_game_form_saves_with_chain(self):
        """ Ensure that new games are populated with a chain """
        form = NewGameForm({'name': 'New Game'})
        game = form.save()
        self.assertEquals(game.chain_set.count(), 1)

class ResponseFormTest(FormTest):
    def test_make_a_valid_message(self):
        """ Simulate making an message from a POST """
        form = ResponseForm(
            data = {'parent': self.parent_message.pk},
            files = {'audio': self.audio},
        )

        self.assertTrue(form.is_valid())

    def test_save_a_valid_message(self):
        """ Save a ResponseForm without validation """
        form = ResponseForm(
            data = {'parent': self.parent_message.pk,
                    'chain': self.chain.pk},
            files = {'audio': self.audio},
        )
        message = form.save()
        self.assertIn(message, self.parent_message.message_set.all())

    def test_validate_form_to_populate_chain(self):
        """ Full clean a ResponseForm and save it """
        form = ResponseForm(
            data = {'parent': self.parent_message.pk},
            files = {'audio': self.audio},
        )

        self.assertTrue(form.is_valid())  # full clean
        message = form.save()
        self.assertEquals(message.chain, self.chain)

    def test_response_forms_require_audio(self):
        message = mommy.make(Message, parent = self.parent_message,
                chain = self.chain)
        form = ResponseForm(data = {'parent': message.pk})
        self.assertFalse(form.is_valid())

class UploadMessageFormTest(FormTest):

    def test_upload_audio_to_empty_message(self):
        message = mommy.make(Message)
        self.assertEqual(message.audio, '')

        form = UploadMessageForm(instance = message,
                                 files = {'audio': self.audio})
        self.assertTrue(form.is_valid())

        updated_message = form.save()
        self.assertNotEqual(updated_message.audio, '')
