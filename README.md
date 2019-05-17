## Restaurant Catalog

#### DESCRIPTION
This is a full-stack web app builded with PYTHON and FLASK.
the purpose of this app is to use a database for managing, trough [SQLAlchemy](https://www.sqlalchemy.org/) library for Python, menus in several restaurants, with the possibility of adding, modifying and removing items into the database.

#### RUNNING THE PROGRAM
1. To get started, I recommend the user use a virtual machine to ensure they are using the same environment that this project was developed on, running on your computer. You can download [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) to install and manage your virtual machine.
Use `vagrant up` to bring the virtual machine online and `vagrant ssh` to login.

2. Download the data provided by Udacity [here](https://www.udacity.com/api/nodes/3612388742/supplemental_media/lotsofmenuspy/download). save the file as lotsofmenus.py. This file should be inside the Vagrant folder.


3. On the vagrant console write:
    * `python3 database_setup.py`
    * `python3 database_employee_setup`
    * `python3 lotsofmenu.py`

4. Now execute: `python3 project.py`
5. Click [here](http://localhost:5000/restaurants) to see this web app in action