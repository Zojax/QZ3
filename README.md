Overview
========

QZ3 is a powerful and flexible python web content management system and framework.
It's a Zope3 based Internet & Intranet CMS. Commissioned & Designed by Quick. Developed and Supported by Zojax.
It's built on Zope technologies to be very robust and flexible with pluggability in mind. The zope component architecture is used everywhere in QZ3 so any component in the system can be added or replaced.

For detailed documentation please visit [docs folder](https://github.com/Zojax/QZ3/docs)

QZ3 is a good choice for medium to large projects, providing an intuitive interface for managing the following types of content:

* standart web-pages
* blog posts
* news
* documents with preview directly on the site
* events with calendar
* forms
* media content
* files
* folders
* email notifications etc.

Features
========

In addition to the usual features provided by Zope such as Zope Component Architecture, templating, code reuse caching and full-featured admin
interface, QZ3 provides the following:

* WYSIWYG content editing using TinyMCE Editor with enriched functionality allowing to insert images and media from a user's PC and from YouTube and Wistia services
* TTW Theme customization
* Hierarchical page navigation
* Save as draft and preview on site
* Scheduled publishing of documents and blog posts
* Per page custom layout layout powered by portlet system
* Tagging system
* SEO friendly URLs
* User accounts and profiles with detailed permissions setting
* Multilingual support
* Commenting blogpost using Facebook or Twitter accounts
* Comments premoderation
* Search engine
* etc.

QZ3 Screenshots
========================

* QZ3 admin dashboard:
![QZ3 admin dashboard](https://raw.githubusercontent.com/Zojax/QZ3/master/docs/imgs/portalsettings.png)

* User's portal settings
![User portal settings](https://raw.githubusercontent.com/Zojax/QZ3/master/docs/imgs/userpreferencies.png)

* Add/edit a web-page form
![Add/edit a web-page form](https://raw.githubusercontent.com/Zojax/QZ3/master/docs/imgs/addwebpage.png)


Browser Support
===============

QZ3 admin interface works with all modern browsers as well as user interface demo template.

Installation
============

The easiest method is to deploy work environment using [virtual machine](https://github.com/Zojax/zojax-dev-box). All the necessary dependences will be installed automatically.
### 1. Before up


On Mac OS X, you do not need to do anything, NFS is already installed.

On Debian/Ubuntu, you just need to install the NFS package:

    $ sudo apt-get install nfs-common nfs-kernel-server


### 2. Adding new box


    $ git clone git@github.com:Zojax/zojax-dev-box.git zojaxbox

    $ cd zojaxbox

    $ vagrant up


### 3. Mounting code from box


    $ vagrant ssh

    (box) $ sudo tee -a /etc/exports <<<'/home/vagrant/zojax      *(rw,async,all_squash,insecure,anonuid=1000,anongid=1000,no_subtree_check)'>/dev/null

    (box) $ sudo service nfs-kernel-server restart

    (box) $ logout


#### for your Ubuntu:


    $ sudo apt-get install nfs-common

    $ mkdir /home/YOUR-USER/workspace/zojax

    $ sudo tee -a /etc/fstab <<<'192.168.33.10:/home/vagrant/zojax  /home/USER/workspace/zojax/files  nfs   rw,async 0 0'>/dev/null

    $ sudo mount /home/YOUR-USER/workspace/zojax


#### for your MacOS:


In Finder, go to: `Go → Connect to Server...` and, in the **Server Address box**, enter:

    nfs://192.168.33.10/home/vagrant/zojax


or use nfs manager

    192.168.33.10:/home/vagrant on /Users/USER/workspace/zojax/files (nfs, nodev, nosuid, automounted, noowners)


### 4. Copy your ssh Key


Assuming you have SSH keys on your host machine, you should be able to copy them to the VM with

    $ scp ~/.ssh/id_rsa vagrant@192.168.33.10:~/.ssh/id_rsa

*password: vagrant*


### 5. git settings


Set up your email in Git:

    (box) $ git config --global user.name "Your Name" # Set your name

    (box) $ git config --global user.email "your-mail@gmail.com" # Set an email


### Vagrant commands


1. Stop VM:

        $ vagrant halt

        [default] Attempting graceful shutdown of linux...


2. Start VM again:

        $ vagrant up


3. Delete VM:

        $ vagrant destroy

## Setting up QZ3


Go to your virtual machine

    $ vagrant ssh

Go to `zojax` folder

    (box) $ cd zojax/

Clone the project:

    (box) $ git clone git@github.com:Zojax/QZ3.git quick.site

    (box) $ cd quick.site

buildout:

    (box) $ /usr/bin/python2.5 bootstrap.py -d -v 1.5.2

    (box) $ bin/buildout


### Work with Instance


Run Instance in the Foreground mode:

    (box) $ bin/instance fg

NOTE: To suspend the instance running in the foreground, press CTRL-c

or you can use:

    (box) $ bin/instance start

    (box) $ bin/instance restart

    (box) $ bin/instance stop

Check the log:

    (box) $ tail -f parts/instance/z3.log -n100


### Open site in a browser


You should  be able now to browse to  URL http://192.168.33.10:8080/ and log in using the default account:

    Login: manager

    Password: V0qGfh0km


Contributing
============

QZ3 is an open source project managed using  the Git version control systems. The repository is hosted on
 [GitHub](https://github.com/Zojax/QZ3), so contributing is as
easy as forking the project on either of these sites and committing
back your enhancements.

Please note the following guidelines for contributing:

* Contributions must be available on a separately named branch
  based on the latest version of the main branch.
* Run the tests before committing your changes. If your changes
  cause the tests to break, they won't be accepted.
* If you are adding new functionality, you must include basic tests
  and documentation.


Support
=======

For all questions or comments, please  please send an email to 'contact@zojax.com'
mailing list. To report a bug or other type of issue, please use the [GitHub issue tracker](https://github.com/Zojax/QZ3/issues).
