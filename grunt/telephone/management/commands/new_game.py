from optparse import make_option

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from telephone.models import Game, Chain

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--name',
            action = 'store',
            help = 'The name of the game'),
        make_option('--nchains',
            action = 'store',
            type = 'int',
            default = 1,
            help = 'Number of chains'),
    )

    def handle(self, name, nchains, **kwargs):
        game = new_game(name = name, nchains = nchains)
        confirmation = 'Initialized {} with {} chains'.format(game, nchains)
        self.stdout.write(confirmation)

def new_game(name = None, nchains = 1):
    game = Game(name = name)
    game.full_clean()
    game.save()

    for _ in range(nchains):
        tmp_chain = Chain(game = game)
        tmp_chain.full_clean()
        tmp_chain.save()

    return game
