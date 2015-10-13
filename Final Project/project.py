import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask import Flask, render_template, request, redirect, jsonify, url_for, current_app
from flask import session as login_session
import json 
import httplib2

Base = declarative_base()
######SENSITIVE INFORMATION - TODO MOVE OUT OF CODE #####

foursquare_client_id = 'SMQNYZFVCIOYIRAIXND2D5SYBLQUOPDB4HZTV13TT22AGACD'

foursquare_client_secret = 'IHBS4VBHYWJL53NLIY2HSVI5A1144GJ3MDTYYY1KLKTMC4BV'

google_api_key = 'AIzaSyBz7r2Kz6x7wO1zV9_O5Rcxmt8NahJ6kos'



#############MODEL############
class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(200), nullable = False)
	picture = Column(String)
    
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
           'name'         : self.name,
           'picture' : self.picture,
       			}


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




engine = create_engine('sqlite:///gourmeet.db')
 

Base.metadata.create_all(engine)

######################
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

#STEP 1 - Add a lunch request to the system
@app.route('/MakeNewLunchRequest/<int:user_id>/<mealType>/<location>/<time>/JSON', methods = ['POST'])
def MakeNewLunchRequest(user_id, mealType, location, time):
	(latitude,longitude) = GetGeocodeLocation(location)
	request = LunchRequest(time = time, location = location, latitude = latitude, longitude = longitude, user_id = user_id, mealType = mealType, filled = False)
	session.add(request)
	session.commit()
	return "OK"

#STEP 2 - View Open Lunch Requests
@app.route('/ViewOpenRequests/JSON/')
def ViewOpenRequests():
	#Return a JSON object with all the open requests in the database
	allRequests = session.query(LunchRequest).filter_by(filled=False).all()
	if allRequests:
		with app.app_context():
			return jsonify(allRequests = [i.serialize for i in allRequests])
	else:
		return "There are currently no open requests"

def ViewRequest(request_id):
	#View a specific open lunch request
	lunchrequest = session.query(LunchRequest).filter_by(id = request_id).one()
	return jsonify(lunchrequest = lunchrequest.serialize)

def ViewLocalRequests(location):
	#v0.1 Feature - Only show nearby open requests
	return

#STEP 3 - Propose a lunch date to another user
def ProposeLunchDate(user_id, LunchRequestID):
	lunchrequest = session.query(LunchRequest).filter_by(id = LunchRequestID).one()
	proposal = Proposal(proposed_by = user_id, proposed_to=lunchrequest.user_id , LunchRequestID = LunchRequestID, filled = False)
	session.add(proposal)
	session.commit()
	return "You made a proposal!"

#STEP 4 - Check to see if you have any lunch date proposals
@app.route("/CheckForPendingRequest/<int:user_id>/JSON")
def CheckForPendingRequest(user_id):
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
@app.route("/ConfirmPendingProposal/<int:proposal_id>/JSON")
def ConfirmPendingProposal(proposal_id):
	acceptedproposal = session.query(Proposal).filter_by(id = proposal_id).one()
	acceptedproposal.filled = True
	lunchrequest = session.query(LunchRequest).filter_by(id = acceptedproposal.LunchRequestID).one()
	lunchrequest.filled = True
	date = MakeADate(lunchrequest.id, acceptedproposal.proposed_to, acceptedproposal.proposed_by)
	session.add(acceptedproposal)
	session.add(lunchrequest)
	session.commit()
	return date

def RejectPendingRequest(request_id):
	rejectedproposal = session.query(Proposal).filter_by(lunchrequest_id = request_id).one()
	session.delete(rejectedproposal)
	session.commit()
	return

#STEP 6 - Check to see if you have any open dates
def CheckForConfirmedDates(user_id):
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
	

###OAUTH STUFF - TO BE EDITED###

# @app.route('/gconnect', methods=['POST'])
# def gconnect():
  
#   #print 'received state of %s' %request.args.get('state')
#   #print 'login_sesion["state"] = %s' %login_session['state']
#   if request.args.get('state') != login_session['state']:
#     response = make_response(json.dumps('Invalid state parameter.'), 401)
#     response.headers['Content-Type'] = 'application/json'
#     return response
  
#   #gplus_id = request.args.get('gplus_id')
#   #print "request.args.get('gplus_id') = %s" %request.args.get('gplus_id')
#   code = request.data
#   print "received code of %s " % code

#   try:
#     # Upgrade the authorization code into a credentials object
#     oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
#     oauth_flow.redirect_uri = 'postmessage'
#     credentials = oauth_flow.step2_exchange(code)
#   except FlowExchangeError:
#     response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
#     response.headers['Content-Type'] = 'application/json'
#     return response
  
#   # Check that the access token is valid.
#   access_token = credentials.access_token
#   url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
#          % access_token)
#   h = httplib2.Http()
#   result = json.loads(h.request(url, 'GET')[1])
#   # If there was an error in the access token info, abort.
#   if result.get('error') is not None:
#     response = make_response(json.dumps(result.get('error')), 500)
#     response.headers['Content-Type'] = 'application/json'

    
#   # Verify that the access token is used for the intended user.
#   gplus_id = credentials.id_token['sub']
#   if result['user_id'] != gplus_id:
#     response = make_response(
#         json.dumps("Token's user ID doesn't match given user ID."), 401)
#     response.headers['Content-Type'] = 'application/json'
#     return response
#   # Verify that the access token is valid for this app.


#   if result['issued_to'] != CLIENT_ID:
#     response = make_response(
#         json.dumps("Token's client ID does not match app's."), 401)
#     print "Token's client ID does not match app's."
#     response.headers['Content-Type'] = 'application/json'
#     return response

  
#   stored_credentials = login_session.get('credentials_access_token')
#   stored_gplus_id = login_session.get('gplus_id')
#   if stored_credentials is not None and gplus_id == stored_gplus_id:
#     response = make_response(json.dumps('Current user is already connected.'),
#                              200)
#     response.headers['Content-Type'] = 'application/json'
    
#   # Store the access token in the session for later use.
#   login_session['provider'] = 'google'
#   login_session['credentials_access_token'] = access_token
#   login_session['gplus_id'] = gplus_id
#   response = make_response(json.dumps('Successfully connected user.', 200))
  
#   print "#Get user info"
#   userinfo_url =  "https://www.googleapis.com/oauth2/v1/userinfo"
#   params = {'access_token': credentials.access_token, 'alt':'json'}
#   answer = requests.get(userinfo_url, params=params)
#   data = json.loads(answer.text)
  
  
#   #login_session['credentials'] = credentials
#   #login_session['gplus_id'] = gplus_id
#   login_session['username'] = data["name"]
#   login_session['picture'] = data["picture"]
#   login_session['email'] = data["email"]
#   #print login_session['email']

#   # see if user exists, if it doesn't make a new one
#   user_id = getUserID(data["email"])
#   if not user_id:
#     user_id = createUser(login_session)
#   login_session['user_id'] = user_id


#   output = ''
#   output +='<h1>Welcome, '
#   output += login_session['username']

#   output += '!</h1>'
#   output += '<img src="'
#   output += login_session['picture']
#   output +=' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
#   flash("you are now logged in as %s"%login_session['username'])
#   return output

#   #Revoke current user's token and reset their login_session.
# @app.route("/gdisconnect")
# def gdisconnect():
  

#   # Only disconnect a connected user.
#   credentials = login_session.get('credentials')
#   if credentials is None:
#     response = make_response(json.dumps('Current user not connected.'), 401)
#     response.headers['Content-Type'] = 'application/json'
#     return response

#   # Execute HTTP GET request to revoke current token.
#   access_token = credentials.access_token
#   url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
#   h = httplib2.Http()
#   result = h.request(url, 'GET')[0]

#   if result['status'] == '200':
#     # Reset the user's session.
    
    

#     response = make_response(json.dumps('Successfully disconnected.'), 200)
#     response.headers['Content-Type'] = 'application/json'
#     return response
#   else:
#     # For whatever reason, the given token was invalid.
#     response = make_response(
#         json.dumps('Failed to revoke token for given user.', 400))
#     response.headers['Content-Type'] = 'application/json'
#     return response


# @app.route('/fbconnect', methods=['POST'])
# def fbconnect():
#   if request.args.get('state') != login_session['state']:
#     response = make_response(json.dumps('Invalid state parameter.'), 401)
#     response.headers['Content-Type'] = 'application/json'
#     return response
#   access_token = request.data
#   print "access token received %s "% access_token

#   #Exchange client token for long-lived server-side token
#  ## GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token} 
#   app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
#   app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
#   url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id,app_secret,access_token)
#   h = httplib2.Http()
#   result = h.request(url, 'GET')[1]

#   #Use token to get user info from API 
#   userinfo_url =  "https://graph.facebook.com/v2.2/me"
#   #strip expire tag from access token
#   token = result.split("&")[0]
  
#   url = 'https://graph.facebook.com/v2.2/me?%s' % token
#   h = httplib2.Http()
#   result = h.request(url, 'GET')[1]
#   #print "url sent for API access:%s"% url
#   #print "API JSON result: %s" % result
#   data = json.loads(result)
#   login_session['provider'] = 'facebook'
#   login_session['username'] = data["name"]
#   login_session['email'] = data["email"]
#   login_session['facebook_id'] = data["id"]
  

#   #Get user picture
#   url = 'https://graph.facebook.com/v2.2/me/picture?%s&redirect=0&height=200&width=200' % token
#   h = httplib2.Http()
#   result = h.request(url, 'GET')[1]
#   data = json.loads(result)

#   login_session['picture'] = data["data"]["url"]
  
#   # see if user exists
#   user_id = getUserID(login_session['email'])
#   if not user_id:
#     user_id = createUser(login_session)
#   login_session['user_id'] = user_id
    
#   output = ''
#   output +='<h1>Welcome, '
#   output += login_session['username']

#   output += '!</h1>'
#   output += '<img src="'
#   output += login_session['picture']
#   output +=' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '


#   flash ("Now logged in as %s" % login_session['username'])
#   return output

# @app.route('/fbdisconnect')
# def fbdisconnect():
#   facebook_id = login_session['facebook_id']
#   url = 'https://graph.facebook.com/%s/permissions' % facebook_id
#   h = httplib2.Http()
#   result = h.request(url, 'DELETE')[1] 
#   return "you have been logged out"

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user


def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)





