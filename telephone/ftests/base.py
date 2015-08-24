import time
import sys
from unipath import Path

from django.conf import settings
from django.core.files import File
from django.test import LiveServerTestCase, override_settings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from grunt.models import Game, Chain, Message

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT, MEDIA_URL = '/media-test/')
class FunctionalTest(LiveServerTestCase):
    def setUp(self):
        super(FunctionalTest, self).setUp()
        self.browser = None
        self.new_user()

    def tearDown(self):
        super(FunctionalTest, self).tearDown()

        if self.browser:
            self.browser.quit()

        TEST_MEDIA_ROOT.rmtree()

    def create_game(self, name, nchains = 1, with_seed = False):
        game = Game.objects.create(name = name)

        for _ in range(nchains):
            chain = Chain.objects.create(game = game) # will use defaults

            if not with_seed:
                Message.objects.create(chain = chain) # ready for upload
            else:
                with open(self.path_to_test_audio(), 'rb') as seed_handle:
                    seed_file = File(seed_handle)
                    message = Message.objects.create(chain = chain, audio = seed_file)
                    message.replicate()

    def new_user(self):
        if self.browser:
            self.browser.quit()

        time.sleep(2)

        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(5)

    def nav_to_games_list(self):
        """ The games list is the home page """
        self.browser.get(self.live_server_url)

    def select_game_items(self):
        """ Simply return the list elements corresponding to available games """
        game_list = self.browser.find_element_by_id('id_game_list')
        return game_list.find_elements_by_tag_name('li')

    def select_game_item_by_game_name(self, name):
        games = self.select_game_items()

        selected = None
        for game in games:
            if game.find_element_by_tag_name('h2').text == name:
                selected = game
                break

        return selected

    def play_game(self, name):
        game_list_item = self.select_game_item_by_game_name(name)
        game_list_item.find_element_by_class_name('play').click()

    def accept_instructions(self):
        self.browser.find_element_by_id('accept').click()

    def simulate_sharing_mic(self):
        """ Execute the operations in micShared() """
        self.browser.execute_script("""
            audioRecorder = true;
            $( "#share" ).addClass("active");
            setPlayer();
        """)

    def path_to_test_audio(self):
        return Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')

    def upload_file(self):
        # Load a file blob to post via AJAX (hack!!)
        create_input_element = ('$( "<input>", {id: "tmpInput", type: "file"})'
                                '.appendTo("body");')
        self.browser.execute_script(create_input_element)

        # Give the file input a real file
        fpath = Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')
        self.browser.find_element_by_id('tmpInput').send_keys(fpath)

        # Take the file from the file input and post it
        self.browser.execute_script('''
            blob = document.getElementById("tmpInput").files[0];
            $( "#tmpInput ").remove();
            sendRecorderMessage(blob);
        ''')

    def wait_for(self, tag = None, id = None, text = None, timeout = 10):
        locator = (By.TAG_NAME, tag) if tag else (By.ID, id)

        if text:
            ec=expected_conditions.text_to_be_present_in_element(locator,text)
        else:
            ec=expected_conditions.presence_of_element_located(locator)

        WebDriverWait(self.browser, timeout).until(
            ec, 'Unable to find element {}'.format(locator))

    def assert_status(self, expected):
        status = self.browser.find_element_by_id('status').text
        self.assertEquals(status, expected)

    def assert_alert_message(self, expected):
        alert_message = self.browser.find_element_by_id('alert').text
        self.assertEquals(alert_message, expected)

    def assert_error_message(self, expected):
        error_message = self.browser.find_element_by_id('message').text
        self.assertEquals(error_message, expected)

    def assert_completion_page(self):
        """ Assert the user made it to the completion page """
        self.assertRegexpMatches(self.browser.current_url, 'complete')

    def assert_completion_code(self, expected):
        code = self.browser.find_element_by_tag_name('code').text
        self.assertEquals(code, expected)

    def assert_audio_src(self, expected):
        audio_src = self.browser.find_element_by_id('sound').get_attribute('src')
        self.assertRegexpMatches(audio_src, expected)

    def inspect_game(self, name):
        game_list_item = self.select_game_item_by_game_name(name)
        game_list_item.find_element_by_class_name('inspect').click()

    def select_svg_messages(self):
        svg = self.browser.find_element_by_tag_name('svg')
        return svg.find_elements_by_css_selector('g.message')

    def assert_filled_message(self, message_group):
        self.assertEquals(message_group.get_attribute('class'), 'message filled')

    def assert_empty_message(self, message_group):
        self.assertEquals(message_group.get_attribute('class'), 'message empty')

    def assert_chain_name(self, expected):
        """ Assert that a chain of the expected name is on the page

        On the inspect view, chains are shown one at a time. In order
        to tell which chain you are looking at, they are given a name
        at the top. This method asserts the name of that chain.
        """
        chain_name = self.browser.find_element_by_id('id_chain_name').text
        self.assertEquals(chain_name, expected)
