#!/usr/bin/env python
import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask import Flask, render_template, request, redirect, jsonify, url_for, current_app
from flask import session as login_session
import json 
import httplib2
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

Base = declarative_base()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


######SENSITIVE INFORMATION - TODO MOVE OUT OF CODE #####

foursquare_client_id = 'SMQNYZFVCIOYIRAIXND2D5SYBLQUOPDB4HZTV13TT22AGACD'

foursquare_client_secret = 'IHBS4VBHYWJL53NLIY2HSVI5A1144GJ3MDTYYY1KLKTMC4BV'

google_api_key = 'AIzaSyBz7r2Kz6x7wO1zV9_O5Rcxmt8NahJ6kos'



######################

app = Flask(__name__)

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = session.query(User).filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/start')
def start():
    return render_template('apis.html')
@app.route('/oauth/<provider>', methods = ['POST'])
def login(provider):
    #STEP 1 - Parse the auth code
    auth_code = request.data
    print "Step 1 - Complete, received auth code %s" % auth_code
    if provider == 'google':
        #STEP 2 - Exchange for a token
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
          
        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            
        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is valid for this app.
        if result['issued_to'] != CLIENT_ID:
            response = make_response(json.dumps("Token's client ID does not match app's."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_credentials = login_session.get('credentials')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_credentials is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('Current user is already connected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        print "Step 2 Complete! Access Token : %s " % credentials.access_token

        #STEP 3 - Find User or make a new one
        
        #Get user info
        userinfo_url =  "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
      
        data = answer.json()

        name = data['name']
        picture = data['picture']
        email = data['email']
        #ADD PROVIDER TO LOGIN SESSION
        provider = 'google'
     
        #see if user exists, if it doesn't make a new one
        user = getUser(email)
        if not user:
            user = createUser(name,email,picture)

        print "Step 3 Complete! - User: %s " % name

        #STEP 4 - Make token
        token = user.generate_auth_token(600)

        print "Step 4 Complete! - API Token: %s" % token

        #STEP 5 - Send back token to the client 
        print "Step 5 - sending off to client...."
        return "Your token is %s " % token
        #return jsonify({'token': token.decode('ascii'), 'duration': 600})
    else:
        return 'Unrecoginized Provider'


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    #if session.query(User).filter_by(username=username).first() is not None:
        #abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

def createUser(name, email, picture):
    user = User(username = name, picture = picture, email = email)
    session.add(user)
    session.commit()
    return user

def getUser(email):
    user = session.query(User).filter_by(email=email).first()
    return user

#STEP 1 - Add a lunch request to the system
@app.route('/MakeNewLunchRequest/<mealType>/<location>/<time>/JSON', methods = ['POST'])
@auth.login_required
def MakeNewLunchRequest(mealType, location, time):
    user_id = g.user.id
    (latitude,longitude) = GetGeocodeLocation(location)
    request = LunchRequest(time = time, location = location, latitude = latitude, longitude = longitude, user_id = user_id, mealType = mealType, filled = False)
    session.add(request)
    session.commit()
    return "OK"

#STEP 2 - View Open Lunch Requests
@app.route('/ViewOpenRequests/JSON/')
@auth.login_required
def ViewOpenRequests():
    #Return a JSON object with all the open requests in the database
    allRequests = session.query(LunchRequest).filter_by(filled=False).all()
    if allRequests:
        with app.app_context():
            return jsonify(allRequests = [i.serialize for i in allRequests])
    else:
        return "There are currently no open requests"

@app.route('/ViewRequest/<int:request_id>/')
@auth.login_required
def ViewRequest(request_id):
    #View a specific open lunch request
    lunchrequest = session.query(LunchRequest).filter_by(id = request_id).one()
    return jsonify(lunchrequest = lunchrequest.serialize)

def ViewLocalRequests(location):
    #v0.1 Feature - Only show nearby open requests
    return

#STEP 3 - Propose a lunch date to another user
@app.route('/ProposeLunchDate/<int:LunchRequestID>/', methods = ['POST'])
@auth.login_required
def ProposeLunchDate(LunchRequestID):
    user_id = g.user.id
    lunchrequest = session.query(LunchRequest).filter_by(id = LunchRequestID).one()
    proposal = Proposal(proposed_by = user_id, proposed_to=lunchrequest.user_id , LunchRequestID = LunchRequestID, filled = False)
    session.add(proposal)
    session.commit()
    return "You made a proposal!"

#STEP 4 - Check to see if you have any lunch date proposals
@app.route("/CheckForPendingRequest/JSON")
@auth.login_required
def CheckForPendingRequest():
    user_id = g.user.id
    #Checks to see if a user has a pending lunch request from another user
    proposals = session.query(Proposal).filter_by(proposed_to = user_id).filter_by(filled=False).all()
    if proposals:
        return jsonify(proposals = [i.serialize for i in proposals])
    else:
        return "You currently have no open lunch proposals"
#View a Specific proposal
def ViewProposal(proposal_id):
    return

#STEP 5 - Accept a lunch proposal and return a date object...or not
@app.route("/ConfirmPendingProposal/<int:proposal_id>/JSON", methods = ['POST'])
@auth.login_required
def ConfirmPendingProposal(proposal_id):
    acceptedproposal = session.query(Proposal).filter_by(id = proposal_id).one()
    if acceptedproposal == None:
        return "The proposal you are trying to fill does not exist."
    if acceptedproposal.filled == True:
        return "This proposal has already been filled" 
    if acceptedproposal.proposed_to != g.user.id:
        return "This proposal was not made to you. You are not authorized to fulfil this request"
    acceptedproposal.filled = True
    lunchrequest = session.query(LunchRequest).filter_by(id = acceptedproposal.LunchRequestID).one()
    lunchrequest.filled = True
    date = MakeADate(lunchrequest.id, acceptedproposal.proposed_to, acceptedproposal.proposed_by)
    session.add(acceptedproposal)
    session.add(lunchrequest)
    session.commit()
    return date

@app.route("/RejectPendingRequest/<int:proposal_id>/JSON")
@auth.login_required
def RejectPendingRequest(request_id):
    rejectedproposal = session.query(Proposal).filter_by(lunchrequest_id = request_id).one()
    session.delete(rejectedproposal)
    session.commit()
    return

#STEP 6 - Check to see if you have any open dates
@app.route("/CheckForConfirmedDates/")
@auth.login_required
def CheckForConfirmedDates():
    user_id = g.user.id
    dates = session.query(Date).filter_by(or_(user1 ==user_id,user2 == user_id)).all()
    if dates:
        return jsonify(dates= [d.serialize for d in dates]) 
    else:
        return "you currently have no open dates"

def ViewDateDetails(date_id):
    date = session.query(Date).filter_by(date_id = date_id).one()
    return jsonify(date.serialize)


#AUXILARY METHODS
def FindARestaurant(latitude, longitude, mealType):
    #Use foursquare API to find a nearby restaurant and return the results
    #https://api.foursquare.com/v2/venues/search?client_id=CLIENT_ID&client_secret=CLIENT_SECRET&v=20130815&ll=40.7,-74&query=sushi
    url = ('https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&v=20130815&ll=%s,%s&query=%s' % (foursquare_client_id, foursquare_client_secret,latitude,longitude,mealType))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])


    #Grab the first restaurant
    restaurant = result['response']['venues'][0]
    venue_id = restaurant['id'] 
    restaurant_name = restaurant['name']
    restaurant_address = restaurant['location']['formattedAddress']
    address = ""
    for i in restaurant_address:
        address += i + " "
    restaurant_address = address
    #Get a  300x300 picture of the restaurant using the venue_id (you can change this by altering the 300x300 value in the URL or replacing it with 'orginal' to get the original picture
    url = ('https://api.foursquare.com/v2/venues/%s/photos?client_id=%s&v=20150603&client_secret=%s' % ((venue_id,foursquare_client_id,foursquare_client_secret)))
    result = json.loads(h.request(url,'GET')[1])
    #Grab the first image
    #if no image available, insert default image url
    if result['response']['photos']['items']:
        firstpic = result['response']['photos']['items'][0]
        prefix = firstpic['prefix']
        suffix = firstpic['suffix']
        imageURL = prefix + "300x300" + suffix
    else:
        imageURL = "http://pixabay.com/get/8926af5eb597ca51ca4c/1433440765/cheeseburger-34314_1280.png?direct"

    restaurantInfo = [{'name':restaurant_name, 'address':restaurant_address, 'image':imageURL}]

    return restaurantInfo

#Calculate the midpoint between two users' locations
def CalculateMidpoint(user1lat,user1long, user2lat, user2long):
    latitude = (user1lat + user2lat) / 2
    longitude = (user1long + user2long) / 2
    return "%s, %s" %(latitude, longitude)

def MakeADate(lunchrequest_id,user1_id, user2_id):
    #Call FindARestaurant to choose the venue
    #Make a date object and send a confirmation to both attendees
    lunchrequest = session.query(LunchRequest).filter_by(id = lunchrequest_id).one()
    restaurant = FindARestaurant(lunchrequest.latitude, lunchrequest.longitude, lunchrequest.mealType)
    date = Date(user1 = user1_id, user2 = user2_id, restaurant = restaurant[0]['name'], restaurant_address = restaurant[0]['address'], restaurant_image = restaurant[0]['image'])
    session.add(date)
    session.commit()
    return jsonify(date=date.serialize)

@app.route('/GetUserInfo/<int:user_id>/JSON')
def GetUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return jsonify(user=user.serialize)

def GetGeocodeLocation(inputString):
    #Use Google Maps to convert a location into Latitute/Longitute coordinates
    #FORMAT: https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=API_KEY
    #Then Store it in the DB
    

    locationString = inputString.replace(" ", "+")
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'% (locationString, google_api_key))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    
    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']



    return (latitude,longitude)





if __name__ == '__main__':
    #if not os.path.exists('db.sqlite'):
     #   db.create_all()

    class User(Base):
        __tablename__ = 'user'
        id = Column(Integer, primary_key=True)
        username = Column(String(32), index=True)
        password_hash = Column(String(64))
        email = Column(String)
        picture = Column(String)

        @property
        def serialize(self):
            """Return object data in easily serializeable format"""
            return {
            'name' : self.name,
            'picture' : self.picture,
                }

        def hash_password(self, password):
            self.password_hash = pwd_context.encrypt(password)

        def verify_password(self, password):
            return pwd_context.verify(password, self.password_hash)

        def generate_auth_token(self, expiration=600):
            s = Serializer(app.secret_key, expires_in=expiration)
            return s.dumps({'id': self.id})

        @staticmethod
        def verify_auth_token(token):
            s = Serializer(app.config['SECRET_KEY'])
            try:
                data = s.loads(token)
            except SignatureExpired:
                return None    # valid token, but expired
            except BadSignature:
                return None    # invalid token
            user = session.query(User).get(data['id'])
            return user
    class LunchRequest(Base):
        __tablename__ = 'lunchrequest'
   
        id = Column(Integer, primary_key=True)
        mealType = Column(String(50), nullable = False)
        city = Column(String)
        location = Column(String)
        latitude = Column(Float, nullable = False)
        longitude = Column(Float, nullable = False)
        user_id = Column(Integer, ForeignKey('user.id'))
        time = Column(String)
        user = relationship(User)
        filled = Column(Boolean)

        @property
        def serialize(self):
            """Return object data in easily serializeable format"""
            return {
               'mealType'         : self.mealType,
               'city' : self.city,
               'latitude' : self.latitude,
               'longitude' : self.longitude,
               'id'           : self.id,
               'time' :self.time,
               'user_id'   : self.user_id
           }


    class Proposal(Base):
        __tablename__ = 'proposal'
        id = Column(Integer, primary_key=True)
        proposed_by = Column(Integer)
        proposed_to = Column(Integer)
        LunchRequestID = Column(Integer, ForeignKey('lunchrequest.id'))
        lunchrequest = relationship(LunchRequest)
        filled = Column(Boolean)

        @property
        def serialize(self):
            """Return object data in easily serializeable format"""
            return {
               'proposed_by'         : self.proposed_by,
               'proposed_to' : self.proposed_to,
               'LunchRequestID' : self.LunchRequestID,
               'filled' : self.filled
           }

    class Date(Base):
        __tablename__ = 'date'
        id = Column(Integer, primary_key=True)
        user1 = Column(String, nullable = False)
        user2 = Column(String, nullable = False)
        #date = Column(String)
        restaurant = Column(String)
        restaurant_address = Column(String)
        restaurant_image = Column(String)
        time = Column(String)
        #accepted = Column(Boolean)

        @property
        def serialize(self):
            """Return object data in easily serializeable format"""
            return {
               'user1'         : self.user1,
               'user2' : self.user2,
               'restaurant' : self.restaurant,
               'restaurant_address' : self.restaurant_address,
               'restaurant_image' : self.restaurant_image,
               'time' : self.time
           }
     
    engine = create_engine('sqlite:///SecureAPI.db')
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.run(debug=True)