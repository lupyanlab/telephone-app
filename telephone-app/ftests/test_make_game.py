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
        self.browser.find_element_by_id('id_submit').click()

        # He sees his new game on the game list page
        games_list = self.browser.find_element_by_id('id_game_list')
        games = games_list.find_elements_by_tag_name('li')
        self.assertEquals(len(games), 1)
        my_new_game = games[0]
        my_new_game_name = my_new_game.find_element_by_tag_name('h2').text
        self.assertEquals(my_new_game_name, new_game_name)
