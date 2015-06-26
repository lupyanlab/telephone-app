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
        self.assert_alert_message("Share your microphone to play.")

        # He shares his microphone
        self.simulate_sharing_mic()

        # Recording is now available
        self.assertNotIn('unavailable', recorder.get_attribute('class'))

        # He creates a recording
        self.upload_file()
        self.wait_for(tag = 'body')

        # His submission was successful,
        # and he lands on the completion page
        self.assert_completion_page()

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

        # The correct audio file is presented on the page
        self.assert_audio_src('0.wav')

        # The recorder isn't available because she hasn't shared her
        # microphone yet
        recorder = self.browser.find_element_by_id('record')
        self.assertIn('unavailable', recorder.get_attribute('class'))
        recorder.click()
        self.assert_alert_message("You have to listen to the message to know what to imitate.")

        # She tries to play the sound, but she has to share her microphone
        # first.
        self.browser.find_element_by_id('listen').click()
        self.assert_alert_message("Share your microphone to play.")

        # She shares her microphone but she still can't record a sound.
        self.simulate_sharing_mic()
        recorder.click()
        self.assert_alert_message("You have to listen to the message to know what to imitate.")

        # She plays the sound
        self.browser.find_element_by_id('listen').click()
        """
        For some reason, the LiveServerTestCase has a problem serving
        from /media-test/ because the audio src is there and accurate
        but in the console it says the file cannot be found.
        """
        #speaker_img = self.browser.find_element_by_id('listen')
        #self.assertIn('active', speaker_img.get_attribute('class'))

        # She records an entry
        self.upload_file()
        self.wait_for(tag = 'body')

        # She sees that her entry was successful:
        # 1. Her status is updated
        # 2. She was taken to the completion page
        # 3. She sees her completion code
        self.assert_completion_page()

    def test_multi_entries(self):
        """ Simulate a player making two entries to two chains """
        game_name = 'Two Chain Game'
        self.create_game(name = game_name, nchains = 2, with_seed = True)

        # She navigates to the game page
        self.nav_to_games_list()
        self.play_game(game_name)

        # She accepts the instructions
        self.accept_instructions()

        # The entry form is ready
        self.assert_audio_src(r'0.wav')

        # She uploads her first entry
        self.upload_file()
        self.wait_for(tag = 'body')

        # Now she listens to a new entry
        self.assert_audio_src(r'0.wav')

        # She makes her second entry
        self.upload_file()
        self.wait_for(tag = 'body')

        # Her entry was successful
        self.assert_completion_page()
