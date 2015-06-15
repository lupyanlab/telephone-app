import time
from unipath import Path

from django.conf import settings

from .base import FunctionalTest

class AjaxTest(FunctionalTest):

    def ajax_post(self):
        # Load a file blob to post via AJAX (hack!!)
        self.browser.execute_script(
            '$( "<input>", {id: "tmpInput", type: "file"}).appendTo("body");'
        )

        fpath = Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')
        self.browser.find_element_by_id('tmpInput').send_keys(fpath)

        self.browser.execute_script('''
            file = document.getElementById("tmpInput").files[0];
            $( "#tmpInput ").remove();
            postEntry(file);
        ''')

        time.sleep(2.5) # wait for success message to go away

    def test_record_seed_message_with_ajax(self):
        """ Simulate a single user submitting an entry via the recorder """
        game_name = 'Real Ajax Game'
        self.create_game(name = game_name)

        # Pierce goes to play the game
        self.nav_to_games_list()
        self.play_game(game_name)

        # He agrees to participate
        self.accept_instructions()

        # He posts an entry via ajax
        self.ajax_post()
        self.wait_for(tag = 'body')

        # She is taken to the completion page
        self.assert_completion_page()

    def test_multi_entries_with_ajax(self):
        """ Simulate sequential AJAX posts """
        game_name = 'Real Ajax Game Two Chains'
        self.create_game(name = game_name, nchains = 2, with_seed = True)

        # She navigates to the game page
        self.nav_to_games_list()
        self.play_game(game_name)

        # She accepts the instructions
        self.accept_instructions()

        # She listens to a seed message
        self.assert_audio_src('0.wav')

        # She records a response
        self.ajax_post()
        self.wait_for(tag = 'body')

        # She listens to another seed message and records a response
        self.assert_audio_src('0.wav')
        self.ajax_post()

        self.assert_completion_page()
