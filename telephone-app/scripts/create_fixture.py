from unipath import Path

from django.conf import settings
from django.core.files import File

from grunt.models import Game, Chain, Message

game = Game.objects.create(name = 'Fixed Game')
chain = game.chain_set.create()

seed = None
to_audio = Path(settings.APP_DIR, 'grunt/tests/media/test-audio.wav')
with open(to_audio, 'rb') as audio:
    seed = chain.message_set.create(audio = File(audio))

entry1 = Message.objects.create(chain = chain, parent = seed)

entry2 = Message(chain = chain, parent = seed)
with open(to_audio, 'rb') as audio:
    entry2.audio = File(audio)
    entry2.save()

entry3 = Message.objects.create(chain = chain, parent = entry2)
