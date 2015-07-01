from .base import FunctionalTest

class MakeGameTest(FunctionalTest):

    def test_make_new_game_via_form(self):
        """ Simulate a user making a new game """
        self.nav_to_games_list()

        # There are no games on the list
        games_list = self.browser.find_element_by_id('id_game_list')
        games = games_list.find_elements_by_tag_name('li')
        self.assertEqual(len(games), 0)

        # He clicks the button to create a new game
        self.browser.find_element_by_id('id_new_game').click()

        # Marcus fills out the new game form
        new_game_name = 'My New Game'
        self.browser.find_element_by_id('id_name').send_keys(new_game_name)
        self.browser.find_element_by_id('submit-id-submit').click()

        # He sees his new game on the game list page
        games_list = self.browser.find_element_by_id('id_game_list')
        games = games_list.find_elements_by_tag_name('li')
        self.assertEquals(len(games), 1)
        my_new_game = games[0]
        my_new_game_name = my_new_game.find_element_by_tag_name('h2').text
        self.assertEquals(my_new_game_name, new_game_name)

    def test_make_game_with_multiple_chains(self):
        """ Make a game with multiple chains """
        self.nav_to_games_list()

        self.browser.find_element_by_id('id_new_game').click()

        new_game_name = 'Two Chain Game'
        num_chains = 2
        self.browser.find_element_by_id('id_name').send_keys(new_game_name)
        # self.browser.find_element_by_id('id_num_chains').send_keys(num_chains)
        self.browser.execute_script(
            'document.getElementById("id_num_chains").setAttribute("value", {});'.format(num_chains)
        )
        self.browser.find_element_by_id('submit-id-submit').click()

        # He sees his new game on the game list page
        games_list = self.browser.find_element_by_id('id_game_list')
        games = games_list.find_elements_by_tag_name('li')
        self.assertEquals(len(games), 1)
        my_new_game = games[0]
        my_new_game_name = my_new_game.find_element_by_tag_name('h2').text
        self.assertEquals(my_new_game_name, new_game_name)

        # He inspects the game and sees the first chain
        self.inspect_game(new_game_name)
        self.assert_chain_name('Chain 0')

        # He clicks next to see the next chain
        self.browser.find_element_by_id('id_next_chain').click()
        self.wait_for(tag = 'body')

        self.assert_chain_name('Chain 1')

        # Clicking "next" again wraps around to first chain. This
        # feature is tested in test_inspect_game.
