import sys

from django.conf import settings
from django.test import LiveServerTestCase, override_settings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from unipath import Path

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')

@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class FunctionalTests(LiveServerTestCase):

    def setUp(self):
        super(FunctionalTests, self).setUp()
        self.browser = None
        self.new_user()

    def tearDown(self):
        super(FunctionalTests, self).tearDown()

        if self.browser:
            self.browser.quit()

        TEST_MEDIA_ROOT.rmtree()

    def create_game(self, name = None, code = None,
                    seeds = ['bark', ], nchain = 1):
        """ Poplulate the database with a game to test interactions """
        from telephone.management.commands.create_game import create_game
        create_game(name = name, code = code, seeds = seeds, nchain = nchain)

    def new_user(self):
        if self.browser:
            self.browser.quit()
        self.browser = webdriver.Firefox()
        self.browser.set_window_size(800, 1000)
        self.browser.implicitly_wait(10)

    def click_on_telephone_game(self, browser = None):
        browser = browser or self.browser
        browser.find_element_by_id('phone').click()

    def click_on_first_game(self, browser = None):
        browser = browser or self.browser
        game_list = browser.find_element_by_id('id_game_list')
        game_list.find_elements_by_tag_name('a')[0].click()

    def accept_instructions(self, browser = None):
        browser = browser or self.browser
        browser.find_element_by_id('accept').click()

    def get_to_entry_screen(self):
        self.browser.get(self.live_server_url)
        self.click_on_telephone_game()
        self.click_on_first_game()
        self.accept_instructions()
        return self.browser.current_url

    def simulate_sharing_mic(self, browser = None):
        browser = browser or self.browser
        browser.execute_script('audioRecorder = true; micShared();')

    def upload_file(self, browser = None):
        browser = browser or self.browser
        # Unhide the file input and give it the path to a file
        browser.execute_script('$( "#id_content" ).attr("type", "file");')
        fpath = Path(settings.APP_DIR, 'telephone/tests/media/test-audio.wav')
        content = browser.find_element_by_id('id_content').send_keys(fpath)
        browser.execute_script('$( "#submit" ).prop("disabled", false);')
        browser.execute_script('audioRecorder = false;')

    def wait_for(self, tag = None, id = None, text = None,
                 browser = None, timeout = 10):
        browser = browser or self.browser

        locator = (By.TAG_NAME, tag) if tag else (By.ID, id)

        if text:
            ec=expected_conditions.text_to_be_present_in_element(locator,text)
        else:
            ec=expected_conditions.presence_of_element_located(locator)

        WebDriverWait(browser, timeout).until(
            ec, 'Unable to find element {}'.format(locator))

    def assert_status(self, expected, browser = None):
        browser = browser or self.browser
        status = browser.find_element_by_id('status').text
        self.assertEquals(status, expected)

    def assert_error_message(self, expected, browser = None):
        browser = browser or self.browser
        error_message = browser.find_element_by_id('message').text
        self.assertEquals(error_message, expected)

    def assert_completion_code(self, expected, browser = None):
        browser = browser or self.browser
        code = browser.find_element_by_tag_name('code').text
        self.assertEquals(code, expected)

    def assert_audio_src(self, expected, browser = None):
        browser = browser or self.browser
        audio_src = browser.find_element_by_id('sound').get_attribute('src')
        self.assertRegexpMatches(audio_src, expected)

def _get_base_folder(host):
    """ Testing against liveserver: Return base dir for site """
    return '~/sites/' + host

def _get_manage_py(host):
    """ Testing against liveserver: Return python and manage.py call """
    return '{path}/virtualenv/bin/python {path}/source/manage.py'.format(
        path = _get_base_folder(host)
    )
