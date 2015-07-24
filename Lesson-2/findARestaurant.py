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
