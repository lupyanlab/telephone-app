Telephone App
=========

Deploy the Telephone Django app to an app server. This project uses ansible for deployment. Ansible can deploy the project to a virtual server using Vagrant. Ansible also deploys the Django app to a production server.

Deploy the app on a virtual server using Vagrant
------

1. Install ansible and vagrant.

2. Clone the repository.

    .. code::

        git clone http://github.com/lupyanlab/telephone-app.git

3. Provision a Telephone App virtual server with vagrant.

   .. code::
        
        vagrant up

   Now you can point your browser to 192.168.33.18 and play around with the
   app.
