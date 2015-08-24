from .base import FunctionalTest

class MultiUserTest(FunctionalTest):

    def submit_entry(self):
        self.upload_file()
        self.wait_for(tag = 'body')

    def simulate_listening_to_sound(self):
        self.browser.find_element_by_id('listen').click()

    def split_seed_message(self, svg):
        messages = svg.find_elements_by_css_selector('g.message')
        self.assertEqual(len(messages), 2)
        seed_message = messages[0]
        seed_message.find_element_by_class_name('split').click()

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
        self.assert_audio_src('0.wav')
        self.simulate_listening_to_sound()
        self.submit_entry()
        self.assert_completion_page()

        # Lynn comes along and plays the same game
        self.new_user()
        self.nav_to_games_list()
        self.play_game(game_name)
        self.accept_instructions()
        self.simulate_sharing_mic()

        # She listens to Marcus's recording (first generation)
        self.assert_audio_src('1.wav')
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
        game_name = 'Two Player Two Chain'
        self.create_game(game_name, nchains = 2, with_seed = True)

        # Pierce inspects the game
        self.nav_to_games_list()
        self.inspect_game(game_name)

        # He sees the first chain
        self.assert_chain_name('Chain 0')

        # He splits the seed message
        svg = self.browser.find_element_by_tag_name('svg')
        self.split_seed_message(svg)

        # He navigates to view the second chain
        self.browser.find_element_by_id('id_next_chain').click()
        self.wait_for(tag = 'body')

        # He splits the seed message for the second chain as well
        self.assert_chain_name('Chain 1')
        svg = self.browser.find_element_by_tag_name('svg')
        self.split_seed_message(svg)

        # Marcus comes along to play the game
        self.new_user()
        self.nav_to_games_list()
        self.play_game(game_name)
        self.accept_instructions()

        # He shares his mic
        self.simulate_sharing_mic()

        # He hears a seed sound and makes a response
        self.assert_audio_src('0.wav')
        self.simulate_listening_to_sound()
        self.submit_entry()

        # He hears another seed sound and makes another response
        self.assert_audio_src('0.wav')
        self.simulate_listening_to_sound()
        self.submit_entry()

        # He gets taken to the completion page
        self.assert_completion_page()

        # Lynn comes along
        self.new_user()
        self.nav_to_games_list()
        self.play_game(game_name)
        self.accept_instructions()

        # She shares her mic
        self.simulate_sharing_mic()

        # She hears the seed sound (not Marcus's sound)
        self.assert_audio_src('0.wav')

        # She makes her response
        self.simulate_listening_to_sound()
        self.submit_entry()

        # She hears another seed sound and makes another response
        self.assert_audio_src('0.wav')
        self.simulate_listening_to_sound()
        self.submit_entry()

        # She's taken to the completion page
        self.assert_completion_page()

        # Pierce comes back to check on progress
        self.new_user()
        self.nav_to_games_list()
        self.inspect_game(game_name)

        svgs = self.browser.find_elements_by_tag_name('svg')
        for chain_svg in svgs:
            messages = chain_svg.find_elements_by_css_selector('g.message')
            self.assertEquals(len(messages), 5)
