from unipath import Path
from shutil import copyfile

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from telephone.models import Game, Seed, Cluster, Chain, Entry

class Command(BaseCommand):
    args = '<seed1 seed2 seed3 ...>'
    help = 'Create seeds'

    def handle(self, *args, **kwargs):
        for arg in args:
            result = create_seed(arg)
            self.stdout.write('Created seed: {}'.format(result.name))

def create_seed(name):
    filepath = Path(settings.APP_DIR, 'telephone/tests/media', name + '.wav')
    seed = Seed(name = name, content = File(open(filepath, 'rb')))
    seed.full_clean()
    seed.save()
    return seed
