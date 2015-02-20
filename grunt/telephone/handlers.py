from unipath import Path

def chain_dir(instance, filename):
    return Path(instance.chain.path(), str(instance) + '.wav')
