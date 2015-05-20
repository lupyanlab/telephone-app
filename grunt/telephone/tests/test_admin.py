
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, override_settings

from telephone.admin import GameAdmin
from telephone.models import Game

class ModelAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.request = None

    def test_default_fields(self):
        game_admin = GameAdmin(Game, self.site)
        admin_form = game_admin.get_form(self.request)
        admin_fields = list(admin_form.base_fields)
        expected_game_fields = [
            'name',
            'type',
            'completion_code',
            'chain_order',
            'status',
        ]
        self.assertEquals(admin_fields, expected_game_fields)
