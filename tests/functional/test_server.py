import os
import threading
import time
from datetime import datetime, timedelta

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from server import app

@pytest.fixture(scope='function', autouse=True)
def set_data(mocker):
    tomorrow = datetime.today() + timedelta(days=1)
    tomorrow = tomorrow.strftime("%Y-%m-%d %H:%M:%S")
    mock_competitions = [
        {
            "name": "Test Competition",
            "date": tomorrow,
            "numberOfPlaces": "25"
        },
        {
            "name": "Spring Festival",
            "date": "2025-04-15 13:00:00",
            "numberOfPlaces": "20"
        }
    ]

    mock_clubs = [
        {
            "name": "Test Club",
            "email": "john@simplylift.co",
            "points": "10"
        },
        {
            "name": "Iron Temple",
            "email": "admin@irontemple.com",
            "points": "15"
        }
    ]

    mocker.patch('server.clubs', mock_clubs)
    mocker.patch('server.competitions', mock_competitions)
    mocker.patch('server.update_clubs', return_value=None)
    mocker.patch('server.update_competitions', return_value=None)

@pytest.mark.usefixtures("set_data")
class TestFunctional:
    @classmethod
    def setup_class(cls):
        app.config['TESTING'] = True
        # use different port in case the "real" server is launched
        app.config['LIVESERVER_PORT'] = 8943
        app.config[
            'DEBUG'] = False

        # Start server on separated thread
        cls.server_thread = threading.Thread(
            target=lambda: app.run(port=app.config['LIVESERVER_PORT']))
        cls.server_thread.daemon = True
        cls.server_thread.start()

        time.sleep(1)

        webdriver_options = Options()
        webdriver_options.add_argument("--headless")
        cls.browser = webdriver.Firefox(options=webdriver_options)
        cls.base_url = f"http://localhost:{app.config['LIVESERVER_PORT']}"

    @classmethod
    def teardown_class(cls):
        cls.browser.quit()

    def login(self):
        self.browser.get(f'{self.base_url}')
        email = self.browser.find_element(By.ID, 'email')
        email.send_keys('john@simplylift.co')
        submit = self.browser.find_element(By.ID, 'submit')
        submit.click()

    def test_index_page(self):
        self.browser.get(f'{self.base_url}')
        assert self.browser.title == 'GUDLFT Registration'

    def test_login_page(self):
        self.login()
        assert "Welcome, john@simplylift.co" in self.browser.page_source

    def test_points_page(self):
        self.browser.get(f'{self.base_url}')
        points_url = self.browser.find_element(By.LINK_TEXT, 'See clubs points')
        points_url.click()
        assert self.browser.title == 'Clubs points'

    def test_book_page(self):
        self.login()
        points_url = self.browser.find_element(By.LINK_TEXT, 'Book Places')
        points_url.click()
        assert 'Test Competition' in self.browser.page_source

    def test_purchase_places(self):
        self.login()
        points_url = self.browser.find_element(By.LINK_TEXT, 'Book Places')
        points_url.click()
        input_places = self.browser.find_element(By.ID, 'places')
        input_places.send_keys('5')
        submit = self.browser.find_element(By.ID, 'submit-places')
        submit.click()
        assert 'Great-booking complete!' in self.browser.page_source


    def test_logout_page(self):
        self.login()
        self.browser.find_element(By.LINK_TEXT, 'Logout').click()
        assert 'Welcome to the GUDLFT Registration Portal!' in self.browser.page_source

