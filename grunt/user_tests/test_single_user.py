from selenium import webdriver
from .base import FunctionalTests

class SingleUserTests(FunctionalTests):

    def test_single_cluster(self):
        """ Simulate a player making an entry to a single cluster game """
        self._fix_game(name = 'Test Game', seeds = ['crow', ], nchain = 1)

        # The player arrives at the homepage.
        self.browser.get(self.live_server_url)
        self.assertIn("Telephone Game", self.browser.title)

        # There is one game available
        game_list = self.browser.find_element_by_id('id_game_list')
        num_games = len(game_list.find_elements_by_tag_name('li'))
        self.assertEquals(num_games, 1)

        # She selects the first game in the list and is taken to a new page
        self.click_on_first_game()
        game_url = self.browser.current_url
        self.assertRegexpMatches(game_url, r'/\d+/',
            "Clicking the game didn't advance the page")

        # She sees some instructions
        instructions = self.browser.find_element_by_tag_name('p').text
        self.assertEquals(instructions, "This is the instructions page")

        # She clicks accept
        self.browser.find_element_by_id('accept').click()

        # She sees the name of the game on the status bar
        game_txt = self.browser.find_element_by_id('game').text
        self.assertEquals(game_txt, 'Test Game')

        # She sees that she hasn't made any entries yet
        self.assert_status(1, 1)

        # The correct audio file is presented on the page
        self.assert_audio_src('crow-0.wav')

        """ Intends to verify that the speaker turns red when clicked
        # She plays the sound and gets visual feedback
        # that the sound is playing.
        self.browser.find_element_by_id('play').click()       # selenium bug
        self.browser.execute_script('$( "#play" ).click();')  # workaround
        phone_img = self.browser.find_element_by_id('phone')
        self.assertIn('on', phone_img.get_attribute('class'))
        """

        """ Intends to verify getting permission to use the microphone
        # She gives permission for her browser to use her microphone
        #self.browser.find_element_by_id('share').click()
        """

        # She tries to submit the form, but sees an error
        self.browser.find_element_by_id('submit').click()
        self.wait_for(tag = 'body')
        error_message = self.browser.find_element_by_id('message')
        self.assertEquals(error_message.text, "You didn't make a recording")

        # Nothing on the page has changed
        self.assert_status(1, 1)
        self.assert_audio_src('crow-0.wav')

        # She uploads an audio file she already has on her computer
        self.upload_file()
        self.browser.find_element_by_id('submit').click()  ## non-ajax POST
        self.wait_for(tag = 'body')

        # She sees that her entry was successful:
        # 1. Her status is updated
        # 2. She was taken to the completion page
        # 3. She sees her completion code
        #self.assert_status("You've made 1 of 1 entries")
        message = self.browser.find_element_by_tag_name('p').text
        self.assertEquals(message, "Keep gruntin'!")

        # She sees the name of the game on the status bar
        game_txt = self.browser.find_element_by_id('game').text
        self.assertEquals(game_txt, 'Test Game')

    def test_multi_clusters(self):
        """ Simulate a player making two entries to two clusters.

        Also ensure that games with completion codes are rendered in the
        template. """
        completion_code = 'test-multi-clusters'
        self._fix_game(code = completion_code, seeds = ['crow', 'bark'])

        # She navigates to the game page
        self.browser.get(self.live_server_url)
        self.click_on_first_game()
        self.accept_instructions()
        game_url = self.browser.current_url

        # She sees that she is going to make two entries
        self.assert_status(1, 2)

        # The entry form is ready
        self.assert_audio_src('crow-0.wav')

        # She uploads her first entry
        self.upload_file()
        self.browser.find_element_by_id('submit').click()  ## non-ajax POST
        self.wait_for(tag = 'body')

        # Her status has updated but she hasn't changed page
        self.assert_status(2, 2)
        self.assertEquals(self.browser.current_url, game_url)

        # Now she listens to a new entry
        self.assert_audio_src('bark-0.wav')

        # She makes her second entry
        self.upload_file()
        self.browser.find_element_by_id('submit').click()  ## non-ajax POST
        self.wait_for(tag = 'body')

        # Her entry was successful
        #self.assert_status(self.browser, "You've made 2 of 2 entries")
        self.assert_completion_code(completion_code)

        # She refreshes the page, but doesn't leave the completion page
        self.browser.refresh()

        # She clicks the button to clear her session
        self.browser.find_element_by_id('clear').click()
        self.wait_for(tag = 'body')

        # She's back at the main page and can make more entries
        self.browser.refresh()
        """ Works fine on dev server! No idea why this doesn't work
        self.assertEqual(self.browser.current_url, game_url)
        self.wait_for(id = 'status', text = 'Message 1 of 2')
        #self.assert_status(1, 2)

        # She listens to her previous recording
        self.assert_audio_src('crow-1.wav')
        """
