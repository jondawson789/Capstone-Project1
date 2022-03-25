from unittest import TestCase
from app import app
from functions import is_player_active

class nba_tests(TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_is_player_active(self):
        