import sys
import os
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
app = Flask(__name__)

DATABASE = 'sqlite:///restaurantmenu.db'

engine = create_engine(DATABASE)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def redirect():
    return redirect(url_for('showRestaurants'))

### RESTAURANT ###

# return restaurant list
@app.route('/restaurants')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurantlist.html', restaurants = restaurants)

# add new restaurant
@app.route('/restaurants/new')
def newRestaurant():
    restaurants = session.query(Restaurant).all()
    # TODO: add function
    return render_template('restaurantlist.html', restaurants = restaurants)

# edit restaurant's information
@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestautant(restaurant_id):
    restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.methods == 'POST':
        # TODO: POST edit function
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editrestaurant.html', restaurant = restaurantToDelete)

# delete restaurant
@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.methods == 'POST':
        # TODO: POST delete function
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleterestaurantconfirmation.html')

### MENU ###

# return menu list
@app.route('/restaurants/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    menu = session.query(MenuItem).filter_by(id = restaurant_id).all()
    return render_template('menu.html', menu = menu)

# add new restaurant
@app.route('/restaurants/<int:restaurant_id>/new')
def newMenuItem(restaurant_id):
    menu = session.query(MenuItem).filter_by(id = restaurant_id).all()
    # TODO: add function
    return render_template('menu.html', menu = menu)

# edit course's information
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    menuToEdit = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    courseToEdit = session.query(menuToEdit).filter_by(id = menu_id)

    if request.methods == 'POST':
        # TODO: POST edit function
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenu.html', course = courseToEdit)

# delete one course
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    menuToDelete = session.query(MenuItem).filter_by(id = restaurant_id)
    if request.methods == 'POST':
        # TODO: POST delete function
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deletemenuconfirmation.html', menu = menu)

### MAIN ###

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    #app.debug = True
    app.run(host='0.0.0.0', port=5000)