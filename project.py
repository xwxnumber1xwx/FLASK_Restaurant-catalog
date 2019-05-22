from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, abort, g
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from flask import session as login_session
import random
import string
from apiclient import discovery
from oauth2client import client
import httplib2
import json
from flask import make_response
import requests
import os
import bleach # -> input validation
from pprint import pprint
import urllib.request
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
app = Flask(__name__)


CLIENT_SECRETS_FILE = './secret_keys/client_secret.json'
SCOPES = " https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid"


@app.route('/')
def index():
    return redirect(url_for('showRestaurants'))

### LOGIN ###


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
        login_session['state'] = state
        return render_template('login.html', STATE=state)
    if request.method == 'POST':
        form = request.form
        email =  bleach.clean(form['email'])
        if email and form['password']:
            password = form['password']
            session = databaseConnection()
            try:
                user = session.query(User).filter_by(email = email).one()
                if user:
                    if user.verify_password(password):
                        print('user logged as %s' % user.name)
                        login_session['username'] = user.name
                        login_session['email'] = user.email
                        login_session['picture'] = ''
                        login_session['user_id'] = user.id
                    else:
                        return jsonify({'message': 'Wrong email or password'}), 401
                else:
                    return jsonify({'message': 'Wrong email or password'}), 401
            except:
                print('exeption')
                return jsonify({'message': 'Wrong email or password'}), 401
        return redirect(url_for('showRestaurants'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    session = databaseConnection()
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = bleach.clean(request.form['name'])
        email = bleach.clean(request.form['email'])
        password = request.form['password']
        if username is None or password is None:
            print("missing arguments")
            abort(400)

        if session.query(User).filter_by(name=username).first() is not None:
            print("existing user")
            user = session.query(User).filter_by(name=username).first()
            # , {'Location': url_for('get_user', id = user.id, _external = True)}
            return jsonify({'message': 'user already exists'}), 200

        user = User(name=username, email=email)
        user.hash_password(password)
        session.add(user)
        session.commit()

        login_session['username'] = username
        login_session['email'] = email
        login_session['picture'] = ''
        login_session['user_id'] = getUserIdDB(email)

        flash(username + ' is now registered')
        return redirect(url_for('showRestaurants'))

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
        response = make_response(json.dumps(
            'aborted for security reason.'), 403)
        response.headers['Content-Type'] = 'application/json'
        return response

    auth_code = request.data

# Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRETS_FILE, SCOPES, auth_code)

    # pprint(credentials.to_json())

# Call Google API
    # http_auth = credentials.authorize(httplib2.Http())
    # service = googleapiclient.discovery.build('oauth2', 'v3', credentials=credentials)


# Get profile info from ID token

    #login_session['userid'] = credentials.id_token['sub']
    login_session['username'] = credentials.id_token['name']
    login_session['email'] = credentials.id_token['email']
    picture_url = credentials.id_token['picture']
    ## Save image on server ##
    urllib.request.urlretrieve(
        picture_url, "static/cache/images/" + login_session['username']+".jpg")
    login_session['picture'] = "static/cache/images/" + \
        login_session['username']+".jpg"
    login_session['provider'] = 'google'

    # check if the user is already on the Database

    user_id = getUserIdDB(login_session['email'])

    if user_id == 'None':
        user_id = createUserDB(login_session)

    login_session['user_id'] = user_id

    flash('You are now connected ad %s' % login_session['username'])

    return redirect(url_for('showRestaurants'))


@app.route('/disconnect')
def disconnect():
    if 'credentials' in login_session:
        del login_session['credentials']
    if 'email' in login_session:
        del login_session['email']
    if 'picture' in login_session:
        if os.path.exists(login_session['picture']):
            os.remove(login_session['picture'])
        del login_session['picture']
    if 'username' in login_session:
        del login_session['username']
    if 'user_id' in login_session:
        del login_session['user_id']
    if 'provider' in login_session:
        del login_session['provider']
    flash('you are logged out')
    return redirect(url_for('showRestaurants'))


def createUserDB(login_session):
    session = databaseConnection()
    newUser = User(name=login_session['username'],
                   email=login_session['email'], picture=login_session['picture'])
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
    if 'username' in login_session:
        return render_template('restaurant.html', restaurants=restaurants, user_id=login_session['user_id'], name=login_session['username'], picture=login_session['picture'])
    else:
        return render_template('publicrestaurant.html', restaurants=restaurants)

# add NEW restaurant
@app.route('/restaurants/new', methods=['GET', 'POST'])
def newRestaurant():
    if 'username' not in login_session:
        return redirect('/login')
    session = databaseConnection()
    if request.method == 'POST':
        restaurant_name = bleach.clean(request.form['name'])
        newRestaurant = Restaurant(name=restaurant_name, user_id=login_session['user_id'])
        session.add(newRestaurant)
        session.commit()
        flash('restaurant %s added on Database' % restaurant_name)
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newrestaurant.html')

# EDIT restaurant's information
@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = databaseConnection()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        edit_name = bleach.clean(request.form['name'])
        if edit_name:
            restaurant.name = edit_name
            session.add(restaurant)
            session.commit()
            flash('restaurant %s updated' % edit_name)
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editrestaurant.html', restaurant=restaurant)

# DELETE restaurant
@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    if 'username' not in login_session:
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
    if 'username' not in login_session:
        return render_template('publicmenu.html', menu=menu, restaurant=restaurant, restaurant_id=restaurant_id)
    else:
        return render_template('menu.html', menu=menu, restaurant=restaurant, restaurant_id=restaurant_id, user_id=login_session['user_id'], name=login_session['username'], picture=login_session['picture'])

# add NEW Menu Item
@app.route('/restaurants/<int:restaurant_id>/new',  methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = databaseConnection()
    if request.method == 'POST':
        form = request.form
        item_name = bleach.clean(form['name'])
        item_price = bleach.clean(form['price'])
        item_description = bleach.clean(form['description'])
        item_course = bleach.clean(form['course'])
        if item_name and item_price and item_course:
            newItem = MenuItem(name = item_name, price=item_price,
                            description=item_description, course=item_course, restaurant_id=restaurant_id, user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            flash('%s added on Database' % item_name)
        else:
            flash('Something went wrong, please fill in all fields')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        courses = session.query(MenuItem).group_by('course').all()
        return render_template('newmenuitem.html', restaurant_id=restaurant_id, courses=courses)

# EDIT menu Item information
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = databaseConnection()
    itemToEdit = session.query(MenuItem).filter_by(
        id=menu_id, restaurant_id=restaurant_id).one()

    if request.method == 'POST':
        form = request.form
        item_name = bleach.clean(form['name'])
        item_price = bleach.clean(form['price'])
        item_description = bleach.clean(form['description'])
        item_course = bleach.clean(form['course'])
        if item_name:
            itemToEdit.name = item_name
        if item_price:
            itemToEdit.price = item_price
        if item_description:
            itemToEdit.description = item_description
        if item_course:
            itemToEdit.course = item_course
        session.add(itemToEdit)
        session.commit()
        flash('%s updated' % item_name)
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        courses = session.query(MenuItem).group_by('course').all()
        return render_template('editmenu.html', restaurant_id=restaurant_id, item=itemToEdit, courses=courses)

# DELETE one course
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
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


@auth.verify_password
def verify_password(email_or_token, password):
    session = databaseConnection()
    # Try to see if it's a token first
    user_id = User.verify_auth_token(email_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(email=email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

# List of all restaurants
@app.route('/api/v1/restaurants/JSON', methods=['POST', 'GET'])
@auth.login_required
def JSONRestaurants():
    session = databaseConnection()
    if request.method == 'GET':
        restaurants = session.query(Restaurant).all()
        return jsonify(Restaurant=[i.serialize for i in restaurants])
    elif request.method == 'POST':
        name= bleach.clean(request.json.get('name'))
        user_id= bleach.clean(request.json.get('user_id'))
        if name and user_id:
            restaurant = Restaurant(name=name, user_id=user_id)
            session.add(restaurant)
            session.commit()
            return jsonify(Restaurant=[restaurant.serialize])


# Menu of one restaurant
@app.route('/api/v1/restaurants/<int:restaurant_id>/menu/JSON')
@auth.login_required
def JSONmenu(restaurant_id):
    session = databaseConnection()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItem=[i.serialize for i in items])

# one item from menu
@app.route('/api/v1/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
@auth.login_required
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
