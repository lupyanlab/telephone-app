Telephone App
=============

Deploy the Telephone Django app to an app server. This project uses ansible for deployment. Ansible can deploy the project to a virtual server using Vagrant. Ansible also deploys the Django app to a production server.

Download a game
---------------

Games can be downloaded from the command line.

.. code::

    $ invoke download_game "My Game"

The command first tries to download the game from an S3 bucket. If it doesn't
exist, it is created on the server and pushed to S3 by running the ansible
playbook "download_game.yml".

Deploy the app on a virtual server using Vagrant
------------------------------------------------

1. Install ansible and vagrant.

2. Clone the repository.

    .. code::

        git clone http://github.com/lupyanlab/telephone-app.git

3. Provision a Telephone App virtual server with vagrant.

   .. code::
        
        vagrant up

   Now you can point your browser to 192.168.33.18 and play around with the
   app.

   This is a fork of the ansible-django-stack project <https://github.com/jcalazan/ansible-django-stack>.

