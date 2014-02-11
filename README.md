Project brief description
=========================

This application is an open-source version of Zope 3 based CMS used for sites developed by Zojax.


How to deploy
=============

The most convenient way is to use [virtual machine](https://github.com/Zojax/zojax-dev-box "zojax virtual machine"). All the necessary dependences will be installed automatically.


Installation Process
====================

Clone the project:

    $ git clone git@github.com:Zojax/zojax.cms.git quick.site

    $ cd quick.site

buildout:

    $ /usr/bin/python2.5 bootstrap.py -d -v 1.5.2

    $ bin/buildout


Work with Instance
==================

Run Instance in the Foreground mode:

    $ bin/instance fg

NOTE: To suspend the instance running in the foreground, press CTRL-c

or you can use:

    $ bin/instance start

    $ bin/instance restart

    $ bin/instance stop

Check the log:

    $ tail -f parts/instance/z3.log -n100


Open site in a browser
======================

Go to instance URL http://localhost:8080/ and log in

    Login: manager

    Password: V0qGfh0km
