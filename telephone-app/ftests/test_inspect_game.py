from .base import FunctionalTest

class InspectGameTest(FunctionalTest):

    def test_upload_seed(self):
        """ Simulate uploading a seed to an empty game via the inspect view """
        game_name = 'Empty Game'

        # Simulate creating a game
        self.create_game(name = game_name)

        # Marcus clicks through from the homepage to the inspect view.
        self.nav_to_games_list()
        self.inspect_game(game_name)

        # He sees that the game has a single chain with a single message.
        messages = self.select_svg_messages()
        self.assertEquals(len(messages), 1)

        # The message doesn't yet have a seed.
        empty_message = messages[0]

        # Click on the upload text to bring up an upload message form.
        upload_text = empty_message.find_element_by_css_selector('text.upload')
        upload_text.click()
        self.wait_for(tag = 'form')

        # He uploads a seed file
        upload_form = self.browser.find_element_by_tag_name('form')
        local_audio_file = self.path_to_test_audio()
        upload_form.find_element_by_id('id_audio').send_keys(local_audio_file)
        upload_form.submit()
        self.wait_for(tag = 'svg')

        # He sees that two sounds are now visible on the inspect page
        messages = self.select_svg_messages()
        self.assertEquals(len(messages), 2)
