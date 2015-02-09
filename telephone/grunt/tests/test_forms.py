
from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from model_mommy import mommy
from unipath import Path

from grunt.forms import EntryForm
from grunt.models import Game, Chain, Entry

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class FormTests(TestCase):

    def setUp(self):
        self.chain = mommy.make(Chain)
        self.entry = mommy.make(Entry, chain = self.chain)

    def tearDown(self):
        TEST_MEDIA_ROOT.rmtree()

    @property
    def _wav(self):
        # something that can be passed in the wav_file field of Entry objects
        sound = Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')
        return File(open(sound, 'r'))

class EntryFormTests(FormTests):

    def test_save_new_entry_through_form(self):
        """ Simulate making an entry from a POST """
        form = EntryForm(
            data = {'chain': self.chain.pk, 'parent': self.entry.pk},
            files = {'content': self._wav}
        )

        self.assertTrue(form.is_valid())
        entry = form.save()
        self.assertEquals(entry.parent, self.entry)
        self.assertIn(entry, self.chain.entry_set.all())

    def test_save_to_filesystem(self):
        form = EntryForm(
            data = {'chain': self.chain.pk, 'parent': self.entry.pk},
            files = {'content': self._wav}
        )

        self.assertTrue(form.is_valid())
        entry = form.save()
        expected_url = "{name}-{generation}.wav".format(
            name = self.chain.cluster, generation = self.entry.generation + 1
        )
        self.assertRegexpMatches(entry.content.url, expected_url)

    def test_parent_url_is_populated_correctly(self):
        """ """
        form = EntryForm(
            data = {'chain': self.chain.pk, 'parent': self.entry.pk},
            files = {'content': self._wav}
        )
        form.save()
        self.assertEquals(form.parent_url(), self.entry.content.url)

    def test_forms_know_game(self):
        """ """
        entry = self.chain.prepare_entry()
        form = EntryForm(instance = entry)
        self.assertEquals(form.game(), entry.chain.cluster.game)

    def test_form_as_context(self):
        entry = self.chain.prepare_entry()
        form = EntryForm(instance = entry)
        expected = {
            'chain': self.chain.pk,
            'parent': self.entry.pk,
            'url': self.entry.content.url,
            'status': form.status(),
        }
        self.assertDictEqual(form.as_context(), expected)
