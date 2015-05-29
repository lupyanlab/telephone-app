from unipath import Path

from django.conf import settings
from django.core.files import File

from telephone.models import Game, Chain, Message

from .base import FunctionalTest

class MakeGameTest(FunctionalTest):
    def create_game(self, **kwargs):
        game = Game.objects.create(**kwargs)
        chain = Chain.objects.create(game = game) # will use defaults
        Message.objects.create(chain = chain)     # ready for upload

    def test_make_new_game_via_form(self):
        """ Simulate a user making a new game """
        self.nav_to_games_list()

        # Marcus sees a single button to create a new game
        games_list = self.browser.find_element_by_id('id_game_list')
        games = games_list.find_elements_by_tag_name('li')
        self.assertEqual(len(games), 1)
        new_game_item = games[0]

        # He clicks the button to create a new game
        new_game_item.find_element_by_tag_name('a').click()

        # Marcus fills out the new game form
        new_game_name = 'My New Game'
        self.browser.find_element_by_id('id_name').send_keys(new_game_name)
        self.browser.find_element_by_id('id_submit').click()

        # He sees his new game on the game list page
        games_list = self.browser.find_element_by_id('id_game_list')
        games = games_list.find_elements_by_tag_name('li')
        self.assertEquals(len(games), 2)
        my_new_game = games[1]
        my_new_game_name = my_new_game.find_element_by_tag_name('h2').text
        self.assertEquals(my_new_game_name, new_game_name)

    def test_upload_seed(self):
        game_name = 'Empty Game'

        # Simulate creating a game
        self.create_game(name = game_name)

        # Marcus clicks through from the homepage to the inspect view.
        self.nav_to_games_list()
        self.inspect_game(game_name)

        # He sees that the game has a single chain with a single message.
        svg = self.browser.find_element_by_tag_name('svg')
        messages = svg.find_elements_by_tag_name('g')
        self.assertEquals(len(messages), 1)

        # The message doesn't yet have a seed.
        empty_message = messages[0]
        empty_message_text_element = empty_message.find_element_by_tag_name('text')
        self.assertEquals(empty_message_text_element.text, 'empty')

        # He clicks the message text to trigger an upload form
        empty_message_text_element.click()
        self.wait_for(tag = 'form')

        # He uploads a seed file
        upload_form = self.browser.find_element_by_tag_name('form')
        local_audio_file = Path(settings.APP_DIR, 'telephone/tests/media/test-audio.wav')
        upload_form.find_element_by_id('id_audio').send_keys(local_audio_file)
        upload_form.submit()
        self.wait_for(tag = 'svg')

        # He sees that two sounds are now visible on the inspect page
        svg = self.browser.find_element_by_tag_name('svg')
        messages = svg.find_elements_by_tag_name('g')
        self.assertEquals(len(messages), 2)

        # The first message now has name
        first_message = messages[0]
        first_message_text_element = first_message.find_element_by_tag_name('text')
        self.assertEquals(first_message_text_element.text, 'message 1')

        # The second message is empty
        second_message = messages[0]
        second_message_text_element = second_message.find_element_by_tag_name('text')
        self.assertEquals(second_message_text_element.text, 'empty')
