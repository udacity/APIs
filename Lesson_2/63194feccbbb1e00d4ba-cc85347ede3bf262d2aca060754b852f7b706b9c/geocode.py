import httplib2
import json

def getGeocodeLocation(inputString):
	#Use Google Maps to convert a location into Latitute/Longitute coordinates
	#FORMAT: https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=API_KEY
    
    google_api_key = "AIzaSyBz7r2Kz6x7wO1zV9_O5Rcxmt8NahJ6kos"

    locationString = inputString.replace(" ", "+")
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'% (locationString, google_api_key))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    

    return result 