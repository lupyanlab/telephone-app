from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from .handlers import chain_dir

class Game(models.Model):
    """ Games comprise one or more Clusters """
    name = models.CharField(blank = True, null = True, max_length = 30)

    status_choices = [('ACTIV', 'active'), ('INACT', 'inactive')]
    status = models.CharField(choices = status_choices, default = 'ACTIV',
                              max_length = 5)

    cluster_order_choices  = [('SEQ', 'sequential'), ('RND', 'random')]
    order = models.CharField(choices = cluster_order_choices, default = 'SEQ',
                             max_length = 3)

    completion_code = models.CharField(blank = True, null = True,
                             max_length = 20)

    def get_absolute_url(self):
        """ Viewing a game is synonymous with playing the game.

        Games are the only model objects that are visible via URL.
        """
        return reverse('play', kwargs = {'pk': self.pk})

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
        """ Parent directory for entries in this game.

        Appended to MEDIA_ROOT.
        """
        return 'game-{pk}'.format(pk = self.pk)

    def __str__(self):
        """ If the game was not created with a name, provide the directory """
        return self.name or self.dir()

class Seed(models.Model):
    """ An Entry with no parent.

    Seeds are stored separately from other Entries. They are used as the first
    entry of new chains as needed.

    TODO: name validation; no spaces or weird stuff allowed
    """
    name = models.CharField(unique = True, max_length = 30)
    content = models.FileField(upload_to = 'seeds/')

    def __str__(self):
        """ The name of the seed.

        str(seed) will be used as the stem name of all entries originating
        from this seed.

            > str(entry) == '{0}-{1}'.format(seed, entry.generation)
        """
        return self.name

class Cluster(models.Model):
    """ A collection of parallel chains.

    A player only contributes to one chain in a cluster.

    TODO: name validation; no spaces or weird stuff allowed
    """
    chain_selection_choices = [
        ('SRT', 'shortest'),
        ('RND', 'random')
    ]
    game = models.ForeignKey(Game)
    name = models.CharField(max_length = 30)
    method = models.CharField(choices = chain_selection_choices, default='SRT',
                              max_length = 3)
    seed = models.ForeignKey(Seed, null = True, blank = True)

    def full_clean(self, *args, **kwargs):
        if not self.name:
            if not self.seed_id:
                pass
            else:
                self.name = self.seed.name
        super(Cluster, self).full_clean(*args, **kwargs)

    def pick_chain(self):
        """ Select a chain.

        Either pick a chain that is tied for the least amount of entries
        (the default), or select a chain at random.

        Players only respond to a single chain in each cluster.

        TODO: exclude chains that are full

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
        """ Parent directory for all chains in this cluster. """
        return self.name or str(self.seed)

    def __str__(self):
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
        chain = Chain(**kwargs)
        _ = chain.full_clean()
        chain.save()
        return chain

    def create_multiple(self, _quantity, **kwargs):
        """ Create multiple chains at once.

        Parameters
        ----------
        _quantity: int, The number of chains to create
        **kwargs: keyword args passed to the Chain constructor

        Returns
        -------
        a list of Chain objects that were saved to the database
        """
        chains = [self.create_with_entry(**kwargs) for _ in range(_quantity)]
        return chains

class Chain(models.Model):
    """ Chains comprise one or more Entries """
    cluster = models.ForeignKey(Cluster)
    seed = models.ForeignKey(Seed)

    objects = ChainManager()

    def full_clean(self, *args, **kwargs):
        """ If a seed wasn't provided, try the seed for the cluster. """
        if not self.seed_id:
            if not self.cluster_id:
                pass  # punt to super()
            elif not self.cluster.seed:
                raise ValidationError('No seed found')
            else:
                self.seed = self.cluster.seed
        super(Chain, self).full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        """ Save the chain and create a seed entry """
        super(Chain, self).save(*args, **kwargs)
        _ = self.create_entry_from_seed()

    def create_entry_from_seed(self):
        """ Create an entry from the seed.

        Returns
        -------
        an Entry object
        """
        if self.entry_set.count() > 0:
            raise ValidationError("This chain already has a seed entry")

        entry = Entry(chain = self, content = self.seed.content.file)
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

    def dir(self):
        """ Directory to hold all entries in this chain. """
        neighbors = self.cluster.chain_set.all()
        position = list(neighbors).index(self)
        return '{ix}-{seed}'.format(ix = position, seed = self.seed)

    def __str__(self):
        return self.dir()

    def path(self):
        """ The path from MEDIA_ROOT to the chain directory. """
        nesting = {
            'game': self.cluster.game.dir(),
            'cluster': self.cluster.dir(),
            'chain': self.dir(),
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
            seed = self.chain.seed, gen = self.generation
        )
