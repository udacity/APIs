import json
import httplib2

#foursquare_client_id = 'PASTE YOUR FOURSQUARE CLIENT ID HERE'
#foursquare_client_secret = 'PASTE YOUR FOURSQUARE CLIENT SECRET HERE'
#google_api_key = 'PASTE YOUR GOOGLE API KEY HERE'

foursquare_client_id = 'SMQNYZFVCIOYIRAIXND2D5SYBLQUOPDB4HZTV13TT22AGACD'

foursquare_client_secret = 'IHBS4VBHYWJL53NLIY2HSVI5A1144GJ3MDTYYY1KLKTMC4BV'

google_api_key = 'AIzaSyBz7r2Kz6x7wO1zV9_O5Rcxmt8NahJ6kos'

def GetGeocodeLocation(inputString):
    #Replace Spaces with '+' in URL
    locationString = inputString.replace(" ", "+")
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'% (locationString, google_api_key))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']
    return (latitude,longitude)

#This function takes in a string representation of a location and cuisine type, geocode the location, and then pass in the latitude and longitude coordinates to the Foursquare API
def findARestaurant(location, mealType):
    latitude, longitude = GetGeocodeLocation(location)
    url = ('https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&v=20130815&ll=%s,%s&query=%s' % (foursquare_client_id, foursquare_client_secret,latitude,longitude,mealType))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    
    #Grab the first restaurant
    restaurant = result['response']['venues'][0]
    venue_id = restaurant['id'] 
    restaurant_name = restaurant['name']
    restaurant_address = restaurant['location']['formattedAddress']
  
    #Format the Restaurant Address into one string
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

    restaurantInfo = {'name':restaurant_name, 'address':restaurant_address, 'image':imageURL}

    return restaurantInfo