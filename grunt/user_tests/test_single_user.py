from selenium import webdriver
from .base import FunctionalTests

class SingleUserTests(FunctionalTests):

    def test_single_entry(self):
        """ Simulate a player making an entry to a single cluster game """
        self.create_game(name = 'Test Game', seeds = ['crow', ], nchain = 1)

        # The player arrives at the homepage.
        self.browser.get(self.live_server_url)
        self.assertIn("Grunt", self.browser.title)

        # She clicks on the telephone and is redirected to the
        # list of available calls.
        self.browser.find_element_by_id('phone').click()
        self.assertRegexpMatches(self.browser.current_url, r'/calls/$')

        # There is one game available
        game_list = self.browser.find_element_by_id('id_game_list')
        num_games = len(game_list.find_elements_by_tag_name('li'))
        self.assertEquals(num_games, 1)

        # She selects the first game in the list and is taken to a new page
        self.click_on_first_game()
        game_url = self.browser.current_url
        self.assertRegexpMatches(game_url, r'/calls/\d+/$')

        # She sees some instructions
        instructions = self.browser.find_element_by_tag_name('p').text
        self.assertEquals(instructions, "This is the instructions page")

        # She clicks accept
        self.browser.find_element_by_id('accept').click()

        # She sees the name of the game on the status bar
        game_txt = self.browser.find_element_by_id('game').text
        self.assertEquals(game_txt, 'Test Game')

        # She sees that she hasn't made any entries yet
        self.assert_status("Message 1 of 1")

        # The correct audio file is presented on the page
        self.assert_audio_src('crow-0.wav')

        # She tries to play the audio but can't
        self.browser.find_element_by_id('listen').click()
        self.assert_error_message("Share your microphone to play")

        # She shares her microphone and the sound becomes available
        self.simulate_sharing_mic()
        speaker = self.browser.find_element_by_id('listen')
        self.assertNotIn('unavailable', speaker.get_attribute('class'))

        # The recorder isn't available because she hasn't listend
        # to the audio yet
        recorder = self.browser.find_element_by_id('record')
        self.assertIn('unavailable', recorder.get_attribute('class'))
        recorder.click()
        self.assert_error_message("You must listen to the sound first.")

        # She plays the sound and gets visual feedback
        # that the sound is playing.
        self.browser.find_element_by_id('listen').click()
        speaker_img = self.browser.find_element_by_id('listen')
        self.assertIn('active', speaker_img.get_attribute('class'))

        # She hasn't made a recording yet so she can't submit
        submit = self.browser.find_element_by_id('submit')
        self.assertIn('true', submit.get_attribute('disabled'))

        # Nothing on the page has changed
        self.assert_status("Message 1 of 1")
        self.assert_audio_src('crow-0.wav')

        # She uploads an audio file she already has on her computer
        self.upload_file()
        self.assertIsNone(submit.get_attribute('disabled'))
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

    def test_multi_entries(self):
        """ Simulate a player making two entries to two clusters.

        Also ensure that games with completion codes are rendered in the
        template. """
        completion_code = 'test-multi-clusters'
        self.create_game(code = completion_code, seeds = ['crow', 'bark'])

        # She navigates to the game page
        self.browser.get(self.live_server_url)
        self.click_on_telephone_game()
        self.click_on_first_game()
        self.accept_instructions()
        game_url = self.browser.current_url

        # She sees that she is going to make two entries
        self.assert_status("Message 1 of 2")

        # The entry form is ready
        self.assert_audio_src('crow-0.wav')

        # She uploads her first entry
        self.upload_file()
        self.browser.find_element_by_id('submit').click()  ## non-ajax POST
        self.wait_for(tag = 'body')

        # Her status has updated but she hasn't changed page
        self.assert_status("Message 2 of 2")
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

        # She clicks the button to go back to the game page
        self.browser.find_element_by_id('return').click()
        self.assertRegexpMatches(self.browser.current_url, r'/calls/$')

        # She tries to play the same game again
        self.click_on_first_game()
        self.assert_completion_code(completion_code)
