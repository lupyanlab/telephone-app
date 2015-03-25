from unipath import Path

def message_dir(instance, filename):
    """ Determine the filename and path for a new audio message """
    return instance.chain.dirpath()
