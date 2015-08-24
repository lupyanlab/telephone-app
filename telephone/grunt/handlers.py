from unipath import Path

def message_path(instance, filename):
    """ Determine the filename and path for a new audio message """
    message_dir = instance.chain.dirpath()
    stem_kwargs = {'generation': instance.generation}
    message_stem = '{generation}.wav'.format(**stem_kwargs)
    return Path(message_dir, message_stem)
