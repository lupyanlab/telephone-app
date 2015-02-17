from optparse import make_option

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from telephone.models import Game, Seed, Cluster, Chain, Entry
from .create_seed import create_seed

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--name',
            action = 'store',
            help = 'The name of the game'),
        make_option('--code',
            action = 'store',
            help = 'Completion code for this game'),
        make_option('--seeds',
            action = 'append',
            help = 'Seeds in game'),
        make_option('--nchain',
            action = 'store',
            type = 'int',
            default = 1,
            help = 'Number of chains in each cluster'),
    )

    def handle(self, *args, **kwargs):
        game = create_game(**kwargs)
        code = game.completion_code
        seeds = game.cluster_set.values_list('seed__name', flat = True)
        self.stdout.write(
            'Game created ({}) with seeds {}'.format(code, seeds)
        )

def create_game(seeds, nchain, name = None, code = None, **kwargs):
    game, _ = Game.objects.get_or_create(
        name = name, completion_code = code
    )
    for seed_name in seeds:
        try:
            seed = Seed.objects.get(name = seed_name)
        except Seed.DoesNotExist:
            seed = create_seed(seed_name)

        cluster, created = Cluster.objects.get_or_create(
            game = game, seed = seed
        )

        if created:
            Chain.objects.create_multiple(
                cluster = cluster, _quantity = nchain
            )
    return game
