
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from telephone.forms import MessageForm
from telephone.models import Game, Chain, Message

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class FormTests(TestCase):
    def setUp(self):
        self.chain = mommy.make(Chain)
        self.message = mommy.make(Message, chain = self.chain)

        fpath = Path(settings.APP_DIR, 'telephone/tests/media/test-audio.wav')
        self.audio = File(open(fpath, 'rb'))

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()

class MessageFormTests(FormTests):
    def test_make_a_message(self):
        """ Simulate making an message from a POST """
        form = MessageForm(
            data = {'chain': self.chain.pk, 'parent': self.message.pk},
            files = {'audio': self.audio}
        )

        self.assertTrue(form.is_valid())
        message = form.save()
        self.assertEquals(message.parent, self.message)
        self.assertIn(message, self.chain.message_set.all())
