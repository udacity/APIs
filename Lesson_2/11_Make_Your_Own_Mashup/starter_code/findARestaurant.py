foursquare_client_id = "YOUR_ID"
foursquare_client_secret = "YOUR_SECRET"


def FindARestaurant(latitude, longitude, mealType):
	#Use foursquare API to find a nearby restaurant and return the results
	#https://api.foursquare.com/v2/venues/search?client_id=CLIENT_ID&client_secret=CLIENT_SECRET&v=20130815&ll=40.7,-74&query=sushi
	url = ('https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&v=20130815&ll=%s,%s&query=%s' % (foursquare_client_id, foursquare_client_secret,latitude,longitude,mealType))
	h = httplib2.Http()
	result = json.loads(h.request(url,'GET')[1])


	#Grab the first restaurant
	
	#Get a  300x300 picture of the restaurant using the venue_id (you can change this by altering the 300x300 value in the URL or replacing it with 'orginal' to get the original picture
  #Grab the first image
  #if no image available, insert default image url
	

	restaurantInfo = [{'name':restaurant_name, 'address':restaurant_address, 'image':imageURL}]

	return restaurantInfo
