import sys
import os
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('showRestaurants'))

### RESTAURANT ###

# SHOW restaurant list
@app.route('/restaurants')
def showRestaurants():
    session = databaseConnection()
    restaurants = session.query(Restaurant).all()
    return render_template('restaurantlist.html', restaurants=restaurants)

# add NEW restaurant
@app.route('/restaurants/new', methods=['GET', 'POST'])
def newRestaurant():
    session = databaseConnection()
    if request.method == 'POST':
        newRestaurant = Restaurant(name=request.form['name'])
        session.add(newRestaurant)
        session.commit()
        # flash('restaurant added on Database')
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newrestaurant.html')

# EDIT restaurant's information
@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    session = databaseConnection()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
            session.add(restaurant)
            session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editrestaurant.html', restaurant=restaurant)

# DELETE restaurant
@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    session = databaseConnection()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleterestaurantconfirmation.html', restaurant=restaurant)

### MENU ###

# SHOW menu
@app.route('/restaurants/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    session = databaseConnection()
    menu = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('menulist.html', menu=menu, restaurant=restaurant, restaurant_id=restaurant_id)

# add NEW Menu Item
@app.route('/restaurants/<int:restaurant_id>/new',  methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    session = databaseConnection()
    if request.method == 'POST':
        form = request.form
        newItem = MenuItem(name=form['name'], price=form['price'],
                           description=form['description'], course=form['course'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        # flash('element added')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        courses = session.query(MenuItem).group_by('course').all()
        return render_template('newmenuitem.html', restaurant_id=restaurant_id, courses = courses)

# EDIT menu Item information
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    session = databaseConnection()
    itemToEdit = session.query(MenuItem).filter_by(
        id=menu_id, restaurant_id=restaurant_id).one()

    if request.method == 'POST':
        form = request.form
        if form['name']:
            itemToEdit.name = form['name']
        if form['price']:
            itemToEdit.price = form['price']
        if form['description']:
            itemToEdit.description = form['description']
        if form['course']:
            itemToEdit.course = form['course']
        session.add(itemToEdit)
        session.commit()
        # flash('Item updated')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        courses = session.query(MenuItem).group_by('course').all()
        return render_template('editmenu.html', restaurant_id=restaurant_id, item=itemToEdit, courses = courses)

# DELETE one course
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    session = databaseConnection()
    item = session.query(MenuItem).filter_by(
        id=menu_id, restaurant_id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuconfirmation.html', item=item, restaurant_id=restaurant_id)

# API Requests

# List of all restaurants
@app.route('/restaurants/JSON')
def JSONRestaurants():
    session = databaseConnection()
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurant =[i.serialize for i in restaurants])

# Menu of one restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def JSONmenu(restaurant_id):
    session = databaseConnection()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItem =[i.serialize for i in items])

# one item from menu
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def JSONitem(restaurant_id, menu_id):
    session = databaseConnection()
    item = session.query(MenuItem).filter_by(id=menu_id, restaurant_id=restaurant_id).one()
    return jsonify(MenuItem =[item.serialize])

# Database Connection
def databaseConnection():
    DATABASE = 'sqlite:///restaurantmenu.db'
    engine = create_engine(DATABASE)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session

### MAIN ###


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
