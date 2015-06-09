from .base import FunctionalTest

class SingleUserTest(FunctionalTest):

    def test_record_seed_message(self):
        """ A player records the first message of an empty game """

        # Simulate creating a game
        game_name = 'Fresh Game'
        self.create_game(name = game_name)

        # Marcus goes to play the game
        self.nav_to_games_list()
        self.play_game(game_name)

        # He agrees to participate in the game
        self.accept_instructions()

        # He tries to make a recording but it's unavailable
        recorder = self.browser.find_element_by_id('record')
        self.assertIn('unavailable', recorder.get_attribute('class'))

        # He tries clicking the recorder but an error message comes up
        recorder.click()
        self.assert_error_message("Share your microphone to play.")

        # He shares his microphone
        self.simulate_sharing_mic()

        # Recording is now available
        self.assertNotIn('unavailable', recorder.get_attribute('class'))

        # He creates a recording
        self.upload_file()
        self.browser.find_element_by_id('submit').click()  ## non-ajax POST
        self.wait_for(tag = 'body')

        # His submission was successful,
        # and he lands on the completion page
        message = self.browser.find_element_by_tag_name('p').text
        self.assertEquals(message, "Keep gruntin'!")

        # He checks to see if his entry made it into the game
        self.nav_to_games_list()
        self.inspect_game(game_name)

        messages = self.select_svg_messages()
        self.assertEquals(len(messages), 2)

    def test_respond_to_seed_message(self):
        """ A player responds to the seed message in a single-chain game """
        game_name = 'Ongoing Game'
        self.create_game(name = game_name, with_seed = True)

        # Lynn checks out the calls page
        self.nav_to_games_list()

        # She inspects the ongoing game
        self.inspect_game(game_name)

        # She sees the seed message and an open response
        messages = self.select_svg_messages()
        self.assertEquals(len(messages), 2)

        # Lynn goes back to the calls page so she can play the game
        self.nav_to_games_list()
        self.play_game(game_name)

        # She agrees to participate
        self.accept_instructions()

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
        game_url = self.nav_to_play()

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
