from unipath import Path

def message_dir(instance, filename):
    if instance.type == 'SEED':
        return 'seeds/{name}.wav'.format(name = instance.name)
    else:
        fullpath_args = {
            'dirname': instance.dirname(),
            'generation': instance.generation,
        }
        return Path('{dirname}/gen-{generation}.wav'.format(**fullpath_args))
