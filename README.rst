Telephone
=========

Simulate the iterative process of evolution.

* telephone: A game of telephone is played by passing a message from person
  to person <http://en.wikipedia.org/wiki/Chinese_whispers>.


Installing locally
------------------

1. Clone the repository.

.. code::

    git clone http://github.com/pedmiston/telephone.git

2. Install a virtualenv and the required packages.

First make a directory to hold the virtualenv packages.

.. code::

    mkdir ~/.venvs
    virtualenv --python=python2.7 ~/.venvs/telephone

Then activate the virtualenv and install the required packages.

.. code::

    ~/.venvs/telephone/bin/activate
    pip install -r requirements.txt

3. Run the django test server.

.. code::

    python manage.py runserver

