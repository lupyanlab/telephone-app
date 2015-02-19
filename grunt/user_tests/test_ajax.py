from .base import FunctionalTests

from unipath import Path
from django.conf import settings

class AjaxTests(FunctionalTests):

    def ajax_post(self, browser = None):
        # Load a file blob to post via AJAX (hack!!)
        browser = browser or self.browser
        browser.execute_script(
            '$( "<input>", {id: "tmpInput", type: "file"}).appendTo("body");'
        )

        fpath = Path(settings.APP_DIR, 'telephone/tests/media/test-audio.wav')
        browser.find_element_by_id('tmpInput').send_keys(fpath)

        browser.execute_script('''
            file = document.getElementById("tmpInput").files[0];
            $( "#tmpInput ").remove();
            postEntry(file);
        ''')

        #self.wait_for(tag = 'h3', browser = browser)  # status text

    def test_ajax_single_cluster(self):
        """ Simulate a single user submitting an entry via the recorder """
        completion_code = 'test-ajax-code'
        self.create_game(name = 'Ajax Game', seeds = ['crow', ], nchain = 1,
                         code = completion_code)

        # She navigates to the game page
        game_url = self.get_to_entry_screen()

        # She sees that she is going to make a single entry
        self.assert_status("Message 1 of 1")

        # The entry form is ready
        self.assert_audio_src('crow-0.wav')

        # She makes her own recording and posts it via AJAX
        self.ajax_post(self.browser)

        # She is taken to the completion page
        self.wait_for(tag = 'p', text = "Your completion code is:")
        self.assert_completion_code(completion_code)

    def test_ajax_two_clusters(self):
        """ Simulate sequential AJAX posts """
        completion_code = 'test-ajax-code-2'
        self.create_game(name = 'Ajax Game 2', seeds = ['bark', 'phone'],
                         nchain = 1, code = completion_code)

        # She navigates to the game page
        game_url = self.get_to_entry_screen()

        # She sees that she is going to make two entries
        self.assert_status("Message 1 of 2")

        # She makes her first recording and her status updates
        self.assert_audio_src('bark-0.wav')
        self.ajax_post(self.browser)
        self.wait_for(id = 'status', text = "Message 2 of 2")

        # She listens to the next entry
        self.assert_audio_src('phone-0.wav')
        self.ajax_post()
        self.wait_for(tag = 'p', text = "Your completion code is:")
        #self.assert_status(self.browser, "You've made 2 of 2 entries")

        # She is taken to the completion page
        self.assert_completion_code(completion_code)
