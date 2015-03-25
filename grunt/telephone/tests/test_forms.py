
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from telephone.forms import ResponseForm, MessageForm
from telephone.models import Game, Chain, Message

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class FormTests(TestCase):
    def setUp(self):
        fpath = Path(settings.APP_DIR, 'telephone/tests/media/test-audio.wav')
        self.audio = File(open(fpath, 'rb'))

        self.chain = mommy.make(Chain)
        self.parent_message = mommy.make(Message, chain = self.chain,
                audio = self.audio)

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()

class ResponseFormTest(FormTests):
    def test_make_a_valid_message(self):
        """ Simulate making an message from a POST """
        form = ResponseForm(
            data = {'parent': self.parent_message.pk},
            files = {'audio': self.audio},
        )

        self.assertTrue(form.is_valid())

    def test_validate_form_to_populate_chain(self):
        form = ResponseForm(
            data = {'parent': self.parent_message.pk},
            files = {'audio': self.audio},
        )
        form.is_valid()  # full clean
        message = form.save()
        self.assertEquals(message.chain, self.chain)

    def test_save_a_valid_message(self):
        form = ResponseForm(
            data = {'parent': self.parent_message.pk,
                    'chain': self.chain.pk},
            files = {'audio': self.audio},
        )
        message = form.save()
        self.assertIn(message, self.parent_message.message_set.all())
