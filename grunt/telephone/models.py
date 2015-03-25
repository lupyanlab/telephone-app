from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models

from .handlers import message_dir

class Game(models.Model):
    """ Top-level control over calls

    Games can be played or inspected. If the game is being played, the
    game determines which call the player should contribute to next.
    If the game is being inspected, the game returns all of the calls
    in the game.
    """
    # The name of the game. Visible to the players, but not used for
    # naming entries or chains. Instead, the int primary key (pk) is
    # used.
    name = models.CharField(blank = True, null = True, max_length = 30)

    # How many calls should be initialized
    num_calls = models.IntegerField(default = 1)
    ## I feel this might be bad practice...

    possible_game_types = [('PUB', 'public'), ('MTK', 'mturk')]
    type = models.CharField(choices = possible_game_types, default = 'PUB',
            max_length = 3)

    # Completion codes are presented to MTurk players
    completion_code = models.CharField(blank = True, null = True,
            max_length = 20)

    # When playing a game, how should the next call be determined?
    call_order_choices  = [('SEQ', 'sequential'), ('RND', 'random')]
    call_order = models.CharField(choices = call_order_choices, default = 'SEQ',
            max_length = 3)

    # Active games are visible
    status_choices = [('ACTIV', 'active'), ('INACT', 'inactive')]
    status = models.CharField(choices = status_choices, default = 'ACTIV',
                              max_length = 5)

    def save(self, *args, **kwargs):
        """ Update the number of calls in the game on save """
        existing_calls = self.call_set.count()
        # don't delete calls on edit/resave
        if existing_calls > self.num_calls:
            raise ValidationError('Calls must be deleted manually')

        super(Game, self).save(*args, **kwargs)

        # create calls as necessary
        for _ in range(self.num_calls - existing_calls):
            self.call_set.create(game = self)

    def get_play_url(self):
        """ URL for playing this game """
        return reverse('play', kwargs = {'pk': self.pk})

    def get_inspect_url(self):
        """ URL for inspecting this game """
        return reverse('inspect', kwargs = {'pk': self.pk})

    def get_absolute_url(self):
        """ By default, games are played when viewed """
        return self.get_play_url()

    def pick_next_call(self, receipts = list()):
        """ Determine which call should be viewed next

        Fails when:
        (a) there are no calls in the game
        (b) there are no calls not in receipts

        Parameters
        ----------
        receipts: list of calls already made, by primary key

        Returns
        -------
        a Call object, determined by call order
        """
        if self.call_set.count() == 0:
            raise Call.DoesNotExist('No calls in game')

        calls = self.call_set.exclude(pk__in = receipts)
        if not calls:
            raise Call.DoesNotExist('All calls have been used')

        if self.call_order == 'RND':
            calls = calls.order_by('?')

        return calls[0]

    # def prepare_entry(self, receipts = list()):
    #     """ Determines the entry for the player
    #
    #     Step 1: Pick a cluster, excluding ones that have already been seen.
    #     Step 2: Pick a chain in that cluster, either the shortest chain or
    #             one selected at random.
    #     Step 3: Prepare the next entry in that chain.
    #
    #     Returns
    #     -------
    #     an Entry object
    #     """
    #     cluster = self.pick_cluster(receipts = receipts)
    #     chain = cluster.pick_chain()
    #     entry = chain.prepare_entry()
    #     return entry

    def dirname(self):
        """ The name of the directory to hold all of this game's calls """
        return 'game-{pk}'.format(pk = self.pk)

    def __str__(self):
        """ If the game was not created with a name, provide the directory """
        return self.name or self.dirname()

class Call(models.Model):
    """ Collection of messages

    Calls run in parallel to others within the same game.
    """
    game = models.ForeignKey(Game)
    num_seeds = models.IntegerField(default = 1)
    sprout_selection_methods = [('SRT', 'shortest'), ('RND', 'random')]
    selection_method = models.CharField(max_length = 3, default = 'SRT')

    def save(self, *args, **kwargs):
        """ Save a new call or edit an existing call

        Ensure that it has the correct number of seed messages before saving.
        """
        existing_seeds = self.message_set.count()
        # don't delete seed messages on edit/resave
        if existing_seeds > self.num_seeds:
            raise ValidationError('Seeds must be deleted manually')

        super(Call, self).save(*args, **kwargs)

        # create seed messages as necessary
        for _ in range(self.num_seeds - existing_seeds):
            self.message_set.create(type = 'SEED', call = self)

    def pick_next_sprout(self):
        """ Determine which sprout message should be viewed next

        Fails when there are no sprouts in the call.

        Returns
        -------
        a Message object, of type == 'SPRT'
        """
        sprouts = self.message_set.filter(type = 'SPRT')
        if sprouts.count() == 0:
            raise Message.DoesNotExist('No sprouts available')

        if self.selection_method == 'SRT':
            sprouts = list(sprouts)
            sprouts = sorted(sprouts, key = lambda msg: msg.generation)
        else:
            # choose a sprout at random
            sprouts = sprouts.order_by('?')

        return sprouts[0]

    def dirname(self):
        """ The name of the directory to hold all of this call's messages """
        path_args = {'game_dir': self.game.dirname(), 'pk': self.pk}
        return '{game_dir}/call-{pk}'.format(**path_args)

class Message(models.Model):
    """ Audio recordings

    Message types
    -------------
    SEED (seed): a message with no parent, generation = 0
    SPRT (sprout): a placeholder for a message, audio = None
    RESP (response): a message
    """
    name = models.CharField(blank = True, null = True, max_length = 30)
    message_types = [
        ('SEED', 'seed'),
        ('RESP', 'response'),
        ('SPRT', 'sprout')
    ]
    type = models.CharField(choices = message_types, default = 'SEED',
            max_length = 4)

    call = models.ForeignKey(Call, blank = True, null = True)
    parent = models.ForeignKey('self', blank = True, null = True)
    generation = models.IntegerField(default = 0, editable = False)
    audio = models.FileField(upload_to = message_dir, blank=True, null=True)

    # def full_clean(self, *args, **kwargs):
    #     """ Validate message type """
    #     super(Message, self).full_clean(*args, **kwargs)
    #
    #     if self.type == 'SEED':
    #         self.call = None
    #         self.parent = None
    #         self.generation = 0
    #         # validate audio
    #
    #     elif self.type == 'RESP':
    #         if not self.call:
    #             raise ValidationError('A response needs to be in a call')
    #
    #         if not self.parent:
    #             raise ValidationError('A response needs a parent message')
    #         self.generation = self.parent.generation + 1
    #         # validate audio
    #
    #     else:  # type == 'SPRT'
    #         if not self.call:
    #             raise ValidationError('A sprout needs to be in a call')
    #
    #         if not self.parent:
    #             raise ValidationError('A sprout needs a parent message')
    #         self.audio = None

    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)

        if self.type == 'RESP':
            sprout = Message(type = 'SPRT', call = self.call, parent = self)
            sprout.full_clean()
            sprout.save()

    def dirname(self):
        if self.type == 'SEED':
            return 'seeds'
        else:
            return self.call.dirname()

    def __str__(self):
        """ The string representation of the entry

        Entries are named based on the seed and the generation.
        """
        return self.pk

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
    content = models.FileField(upload_to = message_dir)
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
