from .base import FunctionalTest

class ViewClusterTest(FunctionalTest):
    def test_view_cluster_with_one_seed(self):
        """ Simulate an admin viewing a cluster with one seed """
        self.create_game(name = 'Viewing Game', seeds = ['crow', ], nchain = 1)

        # The admin goes to the game
        self.nav_to_view()

        # The name of the game is visible in the browser
        game_txt = self.browser.find_element_by_id('game').text
        self.assertEquals(game_txt, 'Viewing Game')

        # The correct seed is visible
        seed = self.browser.find_element_by_id('crow-0')

        # Clicking the seed plays the sound
        seed.click()

        # The seed should have a single sprout
        sprouts = seed.find_elements_by_tag_name('div')
        self.assertEquals(len(sprouts), 1)
