# Setting up QuickZopeCMS


Go to your virtual machine

    $ vagrant ssh

Go to `zojax` folder

    (box) $ cd zojax/

Clone the project:

    (box) $ git clone git@github.com:Zojax/QuickZopeCMS.git quick.site

    (box) $ cd quick.site

buildout:

    (box) $ /usr/bin/python2.5 bootstrap.py -d -v 1.5.2

    (box) $ bin/buildout


## Work with Instance


Run Instance in the Foreground mode:

    (box) $ bin/instance fg

NOTE: To suspend the instance running in the foreground, press CTRL-c

or you can use:

    (box) $ bin/instance start

    (box) $ bin/instance restart

    (box) $ bin/instance stop

Check the log:

    (box) $ tail -f parts/instance/z3.log -n100


## Open site in a browser


Go to instance URL http://192.168.33.10:8080/ and log in

    Login: manager

    Password: V0qGfh0km
