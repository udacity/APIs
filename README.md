# APIs

Udacity course [Designing RESTful APIs](https://www.udacity.com/course/designing-restful-apis--ud388)


## Introduction

### Why take this course

A crucial skill for a back-end or full-stack web developer is the ability to make applications that are easily accessible and understood for other developers. Mobile developers, front-end developers and other back-end and full-stack developers all rely on API endpoints to enhance the functionality of their applications.


### Repository

This code base was meant to supplement the Udacity course for designing RESTful APIs.  Within each directory you will find sample and solution code to the exercises in this course.  Some of this code will require some modification from the user before it is executable on your machine.


## Course lessons

1. **Whats and whys of APIs**
2. **Accessing published APIs: Google Maps and Foursquare**
3. **Creating your own API endpoints with Flask**
4. **Securing your API**
5. **Writing developer-friendly APIs**


## Course materials

### Recommended prior courses

* [Full Stack Foundations](https://www.udacity.com/course/full-stack-foundations--ud088)
* [Authentication & Authorization: OAuth](https://www.udacity.com/course/authentication-authorization-oauth--ud330)


### API Keys for third party providers

This course uses the Google Maps and Foursquare APIs. You will need to create developer accounts and private keys in order to properly use code snippets that rely on these APIs.


### Python modules

To see a list of locally installed Python modules from the command line:

```text
python
>>> help('modules')
```

The code in this repository assumes the following Python modules are installed:

* `flask`
* `flask-httpauth`
* `httplib`
* `itsdangerous`
* `oauth2client`
* `passlib`
* `redis`
* `requests`
* `sqlalchemy`


### Optional virtual machine

A virtual machine can be used to run the lesson from an operating system with a defined configuration. The virtual machine has all the Python modules listed above.


#### Installing the virtual machine

* *Oracle [VirtualBox](https://www.virtualbox.org/wiki/Downloads) Version 5.2.6 r120293 (Qt5.6.3)* - Software that runs special containers called  virtual machines, like Vagrant.
* *[Vagrant](https://www.vagrantup.com/) 2.0.1 with Ubuntu 16.04.3 LTS (GNU/Linux 4.4.0-75-generic i686)* -  Software that provides the Linux operating system in a defined configuration, allowing it to run identically across many personal computers. Linux can then be run as a virtual machine with VirtualBox.
* *[Udacity Virtual Machine configuration](https://github.com/udacity/fullstack-nanodegree-vm)* - Repository from Udacity that configures Vagrant.
	- Instructions are provided [here](https://www.udacity.com/wiki/ud388/vagrant).
	- Install and run Vagrant from within the directory *fullstack-nanodegree-vm/vagrant*.
	- Fork and clone the lesson repository into */vagrant/*.


#### Running the virtual machine

On the Linux command line:

Change into the Vagrant directory (wherever you have it stored):

```bash
$ cd <path>/fullstack-nanodegree-vm/vagrant
```

Start Vagrant (only necessary after computer restart):

```bash
$ vagrant up
```

Log in to Ubuntu:

```bash
$ vagrant ssh
```

Change into the Vagrant directory:

```bash
vagrant@vagrant:~$ cd /vagrant
```
