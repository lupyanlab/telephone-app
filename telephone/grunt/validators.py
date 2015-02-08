import wave
import os
from unipath import Path

from django.conf import settings
from django.core.exceptions import ValidationError

def validate_audio(wav_file):
    try:
        wave.open(wav_file, 'rb')
    except IOError:
        print "IO error"
        raise ValidationError(u'File not found')
    except wave.Error as e:
        # TODO: Figure out how to get model_mommy.mommy.make(Entry) to pass
        # validation
        raise ValidationError(u'This file is not a valid wav file')
