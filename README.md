# Restaurant Catalog

* [Description](##description)
* [Running the program](##running-the-program)
* [Pictures](##pictures)
* [MIT License](#mit-license)

## DESCRIPTION
This is a full-stack web app builded with PYTHON, FLASK and a secure log-in with Google OAuth2 API.
the purpose of this app is to use a database for managing, trough [SQLAlchemy](https://www.sqlalchemy.org/) library for Python, menus in several restaurants, with the possibility of adding, modifying and removing items into the database. Only registered users can create, update or delete their own items in the restaurant database.

## RUNNING THE PROGRAM
1. To get started, I recommend the user use a virtual machine to ensure they are using the same environment that this project was developed on, running on your computer. You can download [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) to install and manage your virtual machine.
Use `vagrant up` to bring the virtual machine online and `vagrant ssh` to login.

2. Download the data provided by Udacity [here](https://www.udacity.com/api/nodes/3612388742/supplemental_media/lotsofmenuspy/download). save the file as lotsofmenus.py. This file should be inside the Vagrant folder.


3. On the vagrant console write:
    * `python3 database_setup.py`
    * `python3 lotsofmenu.py`

4. Now execute: `python3 project.py`
5. Click [here](http://localhost:5000/restaurants) to see this web app in action

## Pictures

![Restaurant list](https://github.com/xwxnumber1xwx/FLASK_Restaurant-catalog/blob/master/design/restaurantlist.jpg)
![Menu List](https://github.com/xwxnumber1xwx/FLASK_Restaurant-catalog/blob/master/design/MenuItem.jpg)
![Sign in](https://github.com/xwxnumber1xwx/FLASK_Restaurant-catalog/blob/master/design/sign-in.jpg)
![Delete item](https://github.com/xwxnumber1xwx/FLASK_Restaurant-catalog/blob/master/design/deleteItem.jpg)
![RESTful Api response](https://github.com/xwxnumber1xwx/FLASK_Restaurant-catalog/blob/master/design/apiresponse.jpg)


## MIT LICENCE

Copyright (c) [2018] [Daniele Caputo]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.