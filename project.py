from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from apiclient import discovery
from oauth2client import client
import httplib2
import json
from flask import make_response
import requests
import os
from pprint import pprint
import urllib.request

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

app = Flask(__name__)

CLIENT_SECRETS_FILE = './secret_keys/client_secret.json'
SCOPES = " https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid"

@app.route('/')
def index():
    return redirect(url_for('showRestaurants'))

### LOGIN ###


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    print(state)
    return render_template('login.html', STATE=state)


# connection with google
@app.route('/googleconnect', methods=['POST'])
def googleConnect():

# check if the STATE is the same server/client. this is needed to control any malicious javascript
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

# prevent CSRF attacks
    if not request.headers.get('X-Requested-With'):
        response = make_response(json.dumps('aborted for security reason.'), 403)
        response.headers['Content-Type'] = 'application/json'
        return response

    auth_code = request.data

# Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(CLIENT_SECRETS_FILE, SCOPES, auth_code)

    #pprint(credentials.to_json())

# Call Google API
    # http_auth = credentials.authorize(httplib2.Http())
    # service = googleapiclient.discovery.build('oauth2', 'v3', credentials=credentials)


# Get profile info from ID token

    #login_session['userid'] = credentials.id_token['sub']
    login_session['username'] = credentials.id_token['name']
    login_session['email'] = credentials.id_token['email']
    login_session['picture'] = credentials.id_token['picture']
    ## Save image on server ##
    urllib.request.urlretrieve(login_session['picture'], "static/cache/images/"+ login_session['username']+".jpg")
    login_session['provider'] = 'google'

    # check if the user is already on the Database

    user_id = getUserIdDB(login_session['email'])

    if user_id == 'None':
        user_id = createUserDB(login_session)

    login_session['user_id'] = user_id

    print('controll token')
    print(credentials.id_token['sub'])

    flash('You are now connected ad %s' % login_session['username'])

    return redirect(url_for('showRestaurants'))

@app.route('/disconnect')
def disconnect():
    login_session['credentials'] = ''
    login_session['email'] = ''
    login_session['picture'] = ''
    if os.path.exists("static/cache/images/"+ login_session['username']+".jpg"):
        os.remove("static/cache/images/"+ login_session['username']+".jpg")
    login_session['username'] = ''
    login_session['user_id'] = ''
    login_session['provider'] = ''
    flash('you are logged out')
    return redirect(url_for('showRestaurants'))

def createUserDB(login_session):
    session = databaseConnection()
    newUser = User(name=login_session['username'], email=login_session['email'], picture="static/cache/images/"+ login_session['username']+".jpg")
    session = databaseConnection()
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfoDB(user_id):
    session = databaseConnection()
    return session.query(User).filter_by(id=user_id).one()


def getUserIdDB(email):
    session = databaseConnection()
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

### RESTAURANT ###

# SHOW restaurant list
@app.route('/restaurants')
def showRestaurants():
    session = databaseConnection()
    restaurants = session.query(Restaurant).all()
    if login_session['username']:
        return render_template('restaurant.html', restaurants=restaurants, user_id=login_session['user_id'], name=login_session['name'], picture = login_session['picture'])
    else:
        return render_template('publicrestaurant.html', restaurants=restaurants)

# add NEW restaurant
@app.route('/restaurants/new', methods=['GET', 'POST'])
def newRestaurant():
    if login_session['username'] == '':
        return redirect('/login')
    session = databaseConnection()
    if request.method == 'POST':
        newRestaurant = Restaurant(name=request.form['name'])
        session.add(newRestaurant)
        session.commit()
        flash('restaurant %s added on Database' % request.form['name'])
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newrestaurant.html')

# EDIT restaurant's information
@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if login_session['username'] == '':
        return redirect('/login')
    session = databaseConnection()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']
            session.add(restaurant)
            session.commit()
            flash('restaurant %s updated' % request.form['name'])
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editrestaurant.html', restaurant=restaurant)

# DELETE restaurant
@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    if login_session['username'] == '':
        return redirect('/login')
    session = databaseConnection()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        flash('restaurant %s deleted' % restaurant.name)
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
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if login_session['username'] == '':
        return render_template('publicmenu.html', menu=menu, restaurant=restaurant, restaurant_id=restaurant_id)
    else:
        return render_template('menu.html', menu=menu, restaurant=restaurant, restaurant_id=restaurant_id, user_id=login_session['user_id'], name=login_session['name'], picture = login_session['picture'])

# add NEW Menu Item
@app.route('/restaurants/<int:restaurant_id>/new',  methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if login_session['username'] == '':
        return redirect('/login')
    session = databaseConnection()
    if request.method == 'POST':
        form = request.form
        newItem = MenuItem(name=form['name'], price=form['price'],
                           description=form['description'], course=form['course'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash('%s added on Database' % request.form['name'])
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        courses = session.query(MenuItem).group_by('course').all()
        return render_template('newmenuitem.html', restaurant_id=restaurant_id, courses=courses)

# EDIT menu Item information
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    if login_session['username'] == '':
        return redirect('/login')
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
        flash('%s updated' % request.form['name'])
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        courses = session.query(MenuItem).group_by('course').all()
        return render_template('editmenu.html', restaurant_id=restaurant_id, item=itemToEdit, courses=courses)

# DELETE one course
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if login_session['username'] == '':
        return redirect('/login')
    session = databaseConnection()
    item = session.query(MenuItem).filter_by(
        id=menu_id, restaurant_id=restaurant_id).one()
    if request.method == 'POST':
        flash('%s deleted' % item.name)
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
    return jsonify(Restaurant=[i.serialize for i in restaurants])

# Menu of one restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def JSONmenu(restaurant_id):
    session = databaseConnection()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItem=[i.serialize for i in items])

# one item from menu
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def JSONitem(restaurant_id, menu_id):
    session = databaseConnection()
    item = session.query(MenuItem).filter_by(
        id=menu_id, restaurant_id=restaurant_id).one()
    return jsonify(MenuItem=[item.serialize])

# Database Connection


def databaseConnection():
    DATABASE = 'sqlite:///restaurantmenuwithusers.db'
    engine = create_engine(DATABASE)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session

### MAIN ###


if __name__ == '__main__':
# When running locally, disable OAuthlib's HTTPs verification.
# ACTION ITEM for developers:
# When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.secret_key = 'super_secret_key'
    #app.debug = True
    app.run(host='0.0.0.0', port=5000)
