from optparse import make_option

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from grunt.models import Game, Chain

class Command(BaseCommand):
    args = 'The name of the game'

    def handle(self, *args, **options):
        name = args[0]
        game = Game.objects.create(name = name)
        chain = game.chain_set.create()
        chain.message_set.create()
