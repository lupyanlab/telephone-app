from .base import FunctionalTests

class MultiUserTests(FunctionalTests):

    def upload_and_post(self):
        self.upload_file()
        self.browser.find_element_by_id('submit').click()
        self.wait_for(tag = 'body')

    def test_sequential_generations(self):
        """ Simulate two players making entries to the same chain """
        completion_code = 'test-seq-gen'
        self.create_game(name = 'Game Name', seeds = ['crow', ], nchain = 1,
                         code = completion_code)

        # The first player arrives at the homepage and selects the first game
        # in the list.
        game_url = self.get_to_entry_screen()

        # She listens to the seed entry, makes her recording, and uploads it
        self.assert_audio_src('crow-0.wav')
        self.upload_and_post()

        # She is taken to the confirmation page and leaves the site
        self.assert_completion_code(completion_code)
        self.new_user()

        # The second player arrives at the site.
        # She clicks on the same game as player 1
        new_user_url = self.get_to_entry_screen()
        self.assertEquals(new_user_url, game_url,
            "Players weren't playing the same game")

        # She listens to the first player's entry
        self.assert_audio_src('crow-1.wav')

        # She uploads her own entry and is taken to the completion page
        self.upload_and_post()
        self.assert_completion_code(completion_code)

    def test_parallel_chains(self):
        """ Simulate two players making entries in two parallel chains """
        completion_code = 'new-code'
        self.create_game(name = 'Multi Game', seeds = ['bark', ], nchain = 2,
                         code = completion_code)

        # Player 1 joins the game
        game_url = self.get_to_entry_screen()

        # She hears a seed entry
        self.assert_audio_src('bark-0.wav')

        # She makes her entry, is redirected, and quits
        self.upload_and_post()
        self.assert_completion_code(completion_code)
        self.new_user()

        # Player 2 joins the game
        new_user_url = self.get_to_entry_screen()
        self.assertEquals(new_user_url, game_url,
            "Players weren't playing the same game")

        # Since there exists a shorter chain, player 2 hears the same seed
        # entry in another chain
        self.assert_audio_src('bark-0.wav')

        # She makes her entry, is redirected, and quits
        self.upload_and_post()
        self.assert_completion_code(completion_code)
