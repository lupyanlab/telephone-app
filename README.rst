evo-apps
========

Simulate the iterative process of evolution.

grunt
-----

The evolution of sounds.

* telephone: A game of telephone is played by passing a message from person
  to person <http://en.wikipedia.org/wiki/Chinese_whispers>.


Installing locally
==================

1. Clone the repository.

    git clone http://github.com/pedmiston/evo-apps.git

2. Install a virtualenv and the required packages.

    mkdir ~/.venvs  # make a dir for virtual environments
    virtualenv --python=python2.7 ~/.venvs/evo-apps
    ~/.venvs/evo-apps/bin/activate
    pip install -r requirements.txt

3. Create a local_settings.py file.

This is a technique for managing django settings I learned from 
Chuck Martin <http://snakeycode.wordpress.com>. Thanks Chuck!

You need to create a file called "local_settings.py" in the app root. It
needs to define a string variable `LOCATION`. For now, just use 'local'.

    echo "LOCATION = 'local'" > grunt/local_settings.py

4. Run the django test server.

    python manage.py runserver

Installing on a virtual server
==============================

This project uses ansible for deployment, which would not have been possible
without the following repo. Thanks to jcalazan for sharing his work.

<https://github.com/jcalazan/ansible-django-stack>

Just navigate to the ansible directory and type the following command.

    vagrant up

The site should be live at 192.168.33.18 (defaults). You can ssh to 
the virtual machine and look around.

    vagrant ssh

Running the tests
=================

Unit tests for the telephone app are run with the following:

    python manage.py test telephone

Functional tests using the django test server are run with the following:

    python manage.py test tests
