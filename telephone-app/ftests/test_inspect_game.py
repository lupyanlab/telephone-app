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

        seed_message, empty_message = messages
        self.assert_filled_message(seed_message)
        self.assert_empty_message(empty_message)

    def test_split_chain(self):
        """ Upload a seed and split the chain into two branches """
        game_name = 'Two Branch Game'

        # A game with a seed was already created
        self.create_game(game_name, with_seed = True)

        self.nav_to_games_list()
        self.inspect_game(game_name)

        # He sees a single chain with two messages
        messages = self.select_svg_messages()
        self.assertEquals(len(messages), 2)

        # He finds the seed message
        seed_message = messages[0]
        self.assert_filled_message(seed_message)

        # He clicks to split the chain
        seed_message.find_element_by_class_name('split').click()

        self.wait_for(tag = 'body')

        # After the page refreshes, he sees three message
        messages = self.select_svg_messages()
        self.assertEquals(len(messages), 3)

        seed_message = messages.pop(0)
        self.assert_filled_message(seed_message)

        for msg in messages:
            self.assert_empty_message(msg)

    def test_close_chain(self):
        """ Close an empty message """
        game_name = 'Dead End Game'

        self.create_game(game_name, with_seed = True)

        self.nav_to_games_list()
        self.inspect_game(game_name)

        # Lynn sees two messages on the page
        messages = self.select_svg_messages()
        self.assertEquals(len(messages), 2)

        # The child message is empty
        child_message = messages[1]
        self.assert_empty_message(child_message)

        # She closes the child message
        child_message.find_element_by_class_name('delete').click()
        self.wait_for(tag = 'body')

        # After the page refreshes, she sees just one message
        messages = self.select_svg_messages()
        self.assertEquals(len(messages), 1)

        # It's the seed message
        seed_message = messages[0]
        self.assert_filled_message(seed_message)

        # She clicks to create two new chains
        seed_message.find_element_by_class_name('split').click()
        self.wait_for(tag = 'body')

        seed_message = self.select_svg_messages()[0]
        seed_message.find_element_by_class_name('split').click()
        self.wait_for(tag = 'body')

        messages = self.select_svg_messages()
        self.assertEquals(len(messages), 3)

        seed_message = messages.pop(0)
        self.assert_filled_message(seed_message)

        for msg in messages:
            self.assert_empty_message(msg)

    def test_page_through_chains(self):
        """ See one chain at a time, and page to the other chains """
        game_name = 'Two Chain Game'
        self.create_game(game_name, nchains = 2)

        self.nav_to_games_list()
        self.inspect_game(game_name)

        # Pierce sees the first chain in the game
        self.assert_chain_name('Chain 0')

        # There is a single svg element on the page
        svgs = self.browser.find_elements_by_tag_name('svg')
        self.assertEquals(len(svgs), 1)

        # He navigates to the second page
        self.browser.find_element_by_id('id_next_chain').click()
        self.wait_for(tag = 'body')

        # He sees the second chain in the game
        self.assert_chain_name('Chain 1')

        # There is a single svg element on the page
        svgs = self.browser.find_elements_by_tag_name('svg')
        self.assertEquals(len(svgs), 1)

        # He can go backwards to see the previous chain
        self.browser.find_element_by_id('id_previous_chain').click()
        self.wait_for(tag = 'body')
        self.assert_chain_name('Chain 0')

        # If he goes backwards still he wraps around to the last chain
        self.browser.find_element_by_id('id_previous_chain').click()
        self.wait_for(tag = 'body')
        self.assert_chain_name('Chain 1')
