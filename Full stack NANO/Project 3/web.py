import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Item, Base
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

#TODO JSON and XML implementation
#TODO styling

app = Flask(__name__)

#STATIC VARIABLES
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


#SQLAlchemy session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()

#google + client_id
CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

#Upload file check
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#Guard for checking if user is logged in
def logged_in():
    if 'username' not in login_session:
        return False
    else:
        return True
#Clean up method when deleting a category
def delete_items(items):
    for item in items:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image))
        session.delete(item)
        session.commit()

#Login page
@app.route('/login')
def login():
    if 'username' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase +\
                                   string.ascii_lowercase +\
                                   string.digits) for x in xrange(32))
        login_session['state'] = state
        return render_template('others/login.html', STATE=state)
    return redirect("/")

#session creation(AJAX)
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        print "Invalid state parameter."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        print "Failed to upgrade the authorization code."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        print "Token's user ID doesn't match given user ID."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    response = make_response(json.dumps('User connected'),
                                 200)
    return response
#Session destruction
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials']
    print 'In gdisconnect access token is %s' % access_token
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['credentials']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result

    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


#Uploaded image presenting
@app.route('/uploads/<string:filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

#Categories index
@app.route('/categories')
def Categories():
    categories = session.query(Category).all()
    return render_template("categories/index.html", categories=categories)

@app.route('/categories.json')
def CategoriesInJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])

# Show for categories
@app.route('/category/<string:category_name>/')
def ShowCategory(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template("categories/show.html", category=category, items=items)

# new and create for categories
@app.route('/categories/new', methods=['GET', 'POST'])
def NewCategory():
    if logged_in():
        if request.method == 'POST' and request.form["name"]!= "":
            category = Category(name=request.form["name"])
            session.add(category)
            session.commit()
            return redirect(url_for('LatestItems'))
        else:
            return render_template("categories/new.html")
    return redirect(url_for('login'))

#edit category
@app.route('/category/<string:category_name>/edit', methods=['POST', 'GET'])
def EditCategory(category_name):
    if logged_in():
        if request.method == 'GET':
            category = session.query(Category).filter_by(name=category_name).one()
            return render_template("categories/edit.html", category=category)
        else:
            category = session.query(Category).filter_by(name=category_name).one()
            if request.form["name"] != category.name:
                category.name = request.form["name"]
                session.add(category)
                session.commit()
            return redirect(url_for('ShowCategory', category_name=category.name))
    return redirect(url_for('login'))



# delete category
@app.route('/category/<string:category_name>/delete')
def DeleteCategory(category_name):
    if logged_in():
        category = session.query(Category).filter_by(name=category_name).one()
        items = session.query(Item).filter_by(category_id=category.id).all()
        if items:
            delete_items(items)
        session.delete(category)
        session.commit()
        return redirect("/")
    return redirect(url_for('login'))

# latest items and index page
@app.route('/')
@app.route('/items/latest')
def LatestItems():
    items = session.query(Item).all()
    return render_template("items/latest.html", items=items)


# Show category item
@app.route('/category/<string:category_name>/<string:item_name>')
def ShowItem(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(category_id=category.id, name=item_name).one()
    return render_template("items/show.html", item=item, category_name=category_name)


#edit/update for items
@app.route('/<string:category_name>/<string:item_name>/edit', methods=['POST', 'GET'])
def EditItem(category_name, item_name):
    if logged_in():
        if request.method == 'GET':
            category = session.query(Category).filter_by(name=category_name).one()
            categories = session.query(Category).all()
            item = session.query(Item).filter_by(category_id=category.id, name=item_name).one()
            return render_template("items/edit.html", item=item, categories=categories)
        else:
            category = session.query(Category).filter_by(name=category_name).one()
            item = session.query(Item).filter_by(category_id=category.id, name=item_name).one()
            item.name = request.form["name"]
            item.description = request.form["description"]
            image = request.files["image"]
            new_category = session.query(Category).filter_by(id=int(request.form["category"])).one()
            item.category_id = new_category.id
            #Update image if a new one is provided
            if image and image.filename != item.image and allowed_file(image.filename):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image))
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item.image = filename
            session.add(item)
            session.commit()
            return redirect(url_for('ShowItem', category_name=new_category.name, item_name=item.name))
    return redirect(url_for('login'))

# New category item
@app.route('/new_item/', methods=['GET', 'POST'])
def NewItem():
    if logged_in():
        if request.method == 'POST' and request.form["name"]!= "":
            category_name = request.form['category']
            category = session.query(Category).filter_by(name=category_name).one()
            item = Item(category_id=category.id, name=request.form["name"], description=request.form["description"])
            session.add(item)
            session.commit()
            image = request.files["image"]
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item.image = filename
                session.add(item)
                session.commit()
            return redirect(url_for('ShowCategory', category_name=category_name))
        else:
            categories = session.query(Category).all()

            return render_template("items/new.html", categories=categories)
    return redirect(url_for('login'))


#Delete category items
@app.route('/category/<string:category_name>/<string:item_name>/delete', methods=['POST'])
def DeleteItem(category_name, item_name):
    if logged_in():
        category = session.query(Category).filter_by(name=category_name).one()
        item = session.query(Item).filter_by(category_id=category.id, name=item_name).one()
        if request.method == 'POST':
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image))
            session.delete(item)
            session.commit()
            return redirect(url_for('ShowCategory', category_name=category_name))
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.debug = True
    app.secret_key = "secret_key"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.run(host='0.0.0.0', port=3500)
