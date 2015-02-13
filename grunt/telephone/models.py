from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from .handlers import chain_dir

class Game(models.Model):
    """ Games comprise one or more Clusters """
    cluster_order_choices  = [
        ('SEQ', 'sequential'),
        ('RND', 'random'),
    ]
    name = models.CharField(blank = True, null = True, max_length = 30)
    order = models.CharField(choices = cluster_order_choices, default = 'SEQ',
                             max_length = 3)
    completion_code = models.CharField(blank = True, null = True,
                             max_length = 20)

    def get_absolute_url(self):
        """ Viewing a game is synonymous with playing the game.

        Games are the only model objects that are visible via URL.
        """
        return reverse('play_game', kwargs = {'pk': self.pk})

    def prepare_entry(self, receipts = list()):
        """ Determines the entry for the player

        Step 1: Pick a cluster, excluding ones that have already been seen.
        Step 2: Pick a chain in that cluster, either the shortest chain or
                one selected at random.
        Step 3: Prepare the next entry in that chain.

        Returns
        -------
        an Entry object
        """
        cluster = self.pick_cluster(receipts = receipts)
        chain = cluster.pick_chain()
        entry = chain.prepare_entry()
        return entry

    def pick_cluster(self, receipts = list()):
        """ Determine which cluster should be viewed next.

        The record of the clusters each player has contributed to is stored
        in the players session, in a list of "receipts". This method
        excludes clusters that are already in the receipt list and returns
        one of the remaining clusters, possible at random.

        Returns
        -------
        a Cluster object
        """
        clusters = self.cluster_set.exclude(pk__in = receipts)

        if not clusters:
            # signals that all entries have been made
            raise Cluster.DoesNotExist("No more clusters in game")

        if self.order == 'RND':
            clusters = clusters.order_by('?')

        return clusters[0]

    def dir(self):
        """
        game.dir() is used as the name of the directory to hold all clusters,
        chains, and entries in this game.
        """
        return 'game-{pk}'.format(pk = self.pk)

    def __str__(self):
        return self.name or self.dir()

class Seed(models.Model):
    """ An Entry with no parent.

    Seeds are stored separately from other Entries. They are used as the first
    entry of new chains as needed.
    """
    name = models.CharField(unique = True, max_length = 30)
    content = models.FileField(upload_to = 'seeds/')

    def __str__(self):
        """ The string representation of the seed

        str(seed) will be used as the name of the directory to hold any
        clusters that begin with this seed.

            > str(cluster) == str(seed)

        str(seed) will also be used as the base name of all entries starting
        from this seed.

            > str(entry) == '{0}-{1}'.format(seed, entry.generation)
        """
        return self.name

class Cluster(models.Model):
    """ A collection of parallel chains.

    Parallel chains are non-overlapping in the sense that a single player only
    contributes to one chain in a cluster. Clusters consist of a single chain,
    multiple chains branching from the same seed, or multiple chains branching
    from alternative seeds.

    TODO:
    - add a field for chain depth
    """
    chain_selection_choices = [
        ('SRT', 'shortest'),
        ('RND', 'random')
    ]
    game = models.ForeignKey(Game)
    seed = models.ForeignKey(Seed)
    method = models.CharField(choices = chain_selection_choices, default='SRT',
                              max_length = 3)

    def pick_chain(self):
        """ Select a chain.

        Either pick a chain that is tied for the least amount of entries
        (the default), or select a chain at random.

        Players only respond to a single chain in each cluster.

        TODO:
        - exclude chains that are full

        Returns
        -------
        a Chain object
        """
        if self.chain_set.count() == 0:
            raise Chain.DoesNotExist('No chains in cluster')

        if self.method == 'SRT':
            chains = list(self.chain_set.all())
            chains = sorted(chains, key=lambda ch: ch.entry_set.count())
        else:
            chains = self.chain_set.order_by('?')

        return chains[0]

    def dir(self):
        return str(self.seed)

    def __str__(self):
        """ The string representation of the cluster

        The name of the directory to hold all chains in this cluster.
        """
        return self.dir()

class ChainManager(models.Manager):
    """ Custom methods added to the Chain manager make it easier to spawn
    multiple chains in each cluster.
    """
    def create_with_entry(self, **kwargs):
        """ Create a chain populated with a first entry created from the seed

        Returns
        -------
        a Chain object with a related entry
        """
        chain = self.create(**kwargs)
        _ = chain.create_entry_from_seed()  # the new entry is discarded
        return chain

    def create_multiple(self, _quantity, _with_entry = False, **kwargs):
        """ Create multiple chains at once.

        Parameters
        ----------
        _quantity: int, The number of chains to create
        _with_entry: bool, Should the chains be created with a first entry?
        **kwargs: keyword args passed to the Chain constructor

        Returns
        -------
        a list of Chain objects that were saved to the database
        """
        create = self.create_with_entry if _with_entry else self.create
        chains = [create(**kwargs) for _ in range(_quantity)]
        return chains

class Chain(models.Model):
    """ Chains comprise one or more Entries """
    cluster = models.ForeignKey(Cluster)

    objects = ChainManager()

    def create_entry_from_seed(self):
        """ Create an entry from the seed

        Returns
        -------
        an Entry object
        """
        if self.entry_set.count() > 0:
            raise ValidationError("This chain already has a seed entry")

        entry = Entry(chain = self, content = self.cluster.seed.content.file)
        entry.full_clean()
        entry.save()

        return entry

    def prepare_entry(self):
        """ Prepare the next entry in the chain.

        Prepared entries are populated but not saved to the database. They
        are used for populating and rendering EntryForms.

        Returns
        -------
        an entry instance with chain and parent entry already populated.
        """
        last_entry = self.entry_set.last()
        return Entry(chain = self, parent = last_entry)

    def save(self, *args, **kwargs):
        """ Save the chain and create a seed entry """
        super(Chain, self).save(*args, **kwargs)
        self.create_entry_from_seed()
        
    def __str__(self):
        """ """
        chains_in_cluster = self.cluster.chain_set.all()
        index_in_cluster = list(chains_in_cluster).index(self)
        return '{ix}'.format(ix = index_in_cluster)

    def dir(self):
        """ The directory where entries will be saved

        Returns
        -------
        path, relative to media root
        """
        nesting = {
            'game': self.cluster.game,
            'cluster': self.cluster,
            'chain': self,
        }
        return '{game}/{cluster}/{chain}/'.format(**nesting)


class Entry(models.Model):
    """ Entries are file uploads situated in a particular Chain """
    chain = models.ForeignKey(Chain)
    parent = models.ForeignKey('self', null = True, blank = True)
    content = models.FileField(upload_to = chain_dir)
    generation = models.IntegerField(default = 0, editable = False)

    def full_clean(self, *args, **kwargs):
        """ Custom validation for Entry objects

        If the entry is not a seed entry, a parent entry is required.
        """
        super(Entry, self).full_clean(*args, **kwargs)
        if self.parent:
            self.generation = self.parent.generation + 1
        elif self.chain.entry_set.count() > 0:
            raise ValidationError("This chain already has a seed entry")

    def __str__(self):
        """ The string representation of the entry

        Entries are named based on the seed and the generation.
        """
        return '{seed}-{gen}'.format(
            seed = self.chain.cluster.seed, gen = self.generation
        )
