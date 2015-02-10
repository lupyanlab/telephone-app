from .base import FunctionalTests

class MultiUserTests(FunctionalTests):

    def upload_and_post(self, browser = None):
        browser = browser or self.browser
        self.upload_file(browser)
        browser.find_element_by_id('submit').click()
        self.wait_for(tag = 'body', browser = browser)

    def assert_complete(self, game_url, code, browser = None):
        browser = browser or self.browser
        self.assertRegexpMatches(browser.current_url, game_url + 'complete/')
        self.assert_completion_code(code, browser = browser)

    def test_sequential_generations(self):
        """ Simulate two players making entries to the same chain """
        completion_code = 'test-seq-gen'
        self._fix_game(code = completion_code, seeds = ['crow', ], nchain = 1)

        # The first player arrives at the homepage and selects the first game
        # in the list.
        self.browser.get(self.live_server_url)
        self.click_on_first_game()
        game_url = self.browser.current_url

        # She listens to the seed entry, makes her recording, and uploads it
        self.assert_audio_src('crow-0.wav')
        self.upload_and_post()

        # She is taken to the confirmation page and leaves the site
        self.assert_complete(game_url, completion_code)
        self.new_user()

        # The second player arrives at the site.
        # She clicks on the same game as player 1
        self.browser.get(self.live_server_url)
        self.click_on_first_game()
        self.assertEquals(self.browser.current_url, game_url)

        # She listens to the first player's entry
        self.assert_audio_src('crow-1.wav')

        # She uploads her own entry and is taken to the completion page
        self.upload_and_post()
        self.assert_complete(game_url, completion_code)

    def test_parallel_chains(self):
        """ Simulate two players making entries in two parallel chains """
        completion_code = 'new-code'
        self._fix_game(code = completion_code, seeds = ['bark', ], nchain = 2)

        # Player 1 joins the game
        self.browser.get(self.live_server_url)
        self.click_on_first_game()
        game_url = self.browser.current_url

        # She hears a seed entry
        self.assert_audio_src('bark-0.wav')

        # She makes her entry, is redirected, and quits
        self.upload_and_post()
        self.assert_complete(game_url, completion_code)
        self.new_user()

        # Player 2 joins the game
        self.browser.get(self.live_server_url)
        self.click_on_first_game()
        self.assertEquals(game_url, self.browser.current_url)

        # Since there exists a shorter chain, player 2 hears the same seed
        # entry in another chain
        self.assert_audio_src('bark-0.wav')

        # She makes her entry, is redirected, and quits
        self.upload_and_post()
        self.assert_complete(game_url, completion_code)
