Telephone
=========

Simulate the iterative process of evolution.

grunt
-----

The evolution of sounds.

* telephone: A game of telephone is played by passing a message from person
  to person <http://en.wikipedia.org/wiki/Chinese_whispers>.


Installing locally
==================

1. Clone the repository.

.. code::

    git clone http://github.com/pedmiston/telephone.git

2. Install a virtualenv and the required packages.

.. code::

    mkdir ~/.venvs  # make a dir for virtual environments
    virtualenv --python=python2.7 ~/.venvs/telephone
    ~/.venvs/evo-apps/bin/activate
    pip install -r requirements.txt

3. Run the django test server.

.. code::

    python manage.py runserver

Installing on a virtual server
==============================

This project uses ansible for deployment, which would not have been possible
without the following repo. Thanks to jcalazan for sharing his work.

<https://github.com/jcalazan/ansible-django-stack>

Just navigate to the ansible directory and type the following command.

.. code::

    vagrant up

The site should be live at 192.168.33.18 (defaults). You can ssh to 
the virtual machine and look around.

.. code::

    vagrant ssh

Running the tests
=================

Unit tests for the telephone app are run with the following:

.. code::

    python manage.py test telephone

Functional tests using the django test server are run with the following:

.. code::

    python manage.py test ftests
