import sys

from django.conf import settings
from django.test import LiveServerTestCase, override_settings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from unipath import Path

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

    def new_user(self):
        if self.browser:
            self.browser.quit()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(5)

    def click_on_telephone_game(self):
        self.browser.find_element_by_id('phone').click()

    def nav_to_games_list(self):
        self.browser.get(self.live_server_url)
        self.click_on_telephone_game()

    def select_game_items(self):
        game_list = self.browser.find_element_by_id('id_game_list')
        return game_list.find_elements_by_tag_name('li')

    def select_game_item_by_game_name(self, name):
        games = self.select_game_items()

        get_game_name = lambda g: g.find_element_by_tag_name('h2').text
        matched_games = filter(lambda g: get_game_name(g) == name, games)

        match = matched_games[0]
        return match

    def play_game(self, name):
        game_list_item = self.select_game_item_by_game_name(name)
        game_list_item.find_element_by_class_name('play').click()

    def accept_instructions(self):
        self.browser.find_element_by_id('accept').click()

    def simulate_sharing_mic(self):
        self.browser.execute_script('audioRecorder = true; micShared();')

    def upload_file(self):
        # Unhide the file input and give it the path to a file
        self.browser.execute_script('$( "#id_content" ).attr("type", "file");')
        fpath = Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')
        content = self.browser.find_element_by_id('id_content').send_keys(fpath)
        self.browser.execute_script('$( "#submit" ).prop("disabled", false);')
        self.browser.execute_script('audioRecorder = false;')

    def wait_for(self, tag = None, id = None, timeout = 10):
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

    def assert_error_message(self, expected):
        error_message = self.browser.find_element_by_id('message').text
        self.assertEquals(error_message, expected)

    def assert_completion_code(self, expected):
        code = self.browser.find_element_by_tag_name('code').text
        self.assertEquals(code, expected)

    def assert_audio_src(self, expected):
        audio_src = self.browser.find_element_by_id('sound').get_attribute('src')
        self.assertRegexpMatches(audio_src, expected)

    def inspect_game(self, name):
        game_list_item = self.select_game_item_by_game_name(name)
        game_list_item.find_element_by_class_name('inspect').click()
