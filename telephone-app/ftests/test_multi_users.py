from .base import FunctionalTest

class MultiUserTest(FunctionalTest):

    def submit_entry(self):
        self.upload_file()
        self.browser.find_element_by_id('submit').click()
        self.wait_for(tag = 'body')

    def simulate_listening_to_sound(self):
        self.browser.find_element_by_id('listen').click()

    def test_sequential_generations(self):
        """ Two players contribute to the same chain """

        # Simulate creating a game
        game_name = 'Two Player Game'
        self.create_game(game_name, with_seed = True)

        # Marcus plays the game first
        self.nav_to_games_list()
        self.play_game(game_name)
        self.accept_instructions()
        self.simulate_sharing_mic()
        self.simulate_listening_to_sound()
        self.submit_entry()
        message = self.browser.find_element_by_tag_name('p').text
        self.assertEquals(message, "Keep gruntin'!")


        # Lynn comes along and plays the same game
        self.new_user()
        self.nav_to_games_list()
        self.play_game(game_name)
        self.accept_instructions()
        self.simulate_sharing_mic()

        # She listens to Marcus's recording (second generation)
        self.assert_audio_src('2.wav')
        self.simulate_listening_to_sound()
        self.submit_entry()

        # Pierce comes along to check on the progress
        self.new_user()
        self.nav_to_games_list()
        self.inspect_game(game_name)

        # He sees 3 filled messages and a single open message
        messages = self.select_svg_messages()
        self.assertEquals(len(messages), 4)

        empty_message = messages.pop()
        self.assert_empty_message(empty_message)

        for msg in messages:
            self.assert_filled_message(msg)

    def test_parallel_chains(self):
        """ Simulate two players making entries in two parallel chains """
        completion_code = 'new-code'
        self.create_game(name = 'Multi Game', seeds = ['bark', ], nchain = 2,
                         code = completion_code)

        # Player 1 joins the game
        game_url = self.nav_to_play()

        # She hears a seed entry
        self.assert_audio_src('bark-0.wav')

        # She makes her entry, is redirected, and quits
        self.upload_and_post()
        self.assert_completion_code(completion_code)
        self.new_user()

        # Player 2 joins the game
        new_user_url = self.nav_to_play()
        self.assertEquals(new_user_url, game_url,
            "Players weren't playing the same game")

        # Since there exists a shorter chain, player 2 hears the same seed
        # entry in another chain
        self.assert_audio_src('bark-0.wav')

        # She makes her entry, is redirected, and quits
        self.upload_and_post()
        self.assert_completion_code(completion_code)
