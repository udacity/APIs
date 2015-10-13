from findARestaurant import findARestaurant
from model import Base, Restaurant
from flask import Flask, jsonify, request
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

foursquare_client_id = 'SMQNYZFVCIOYIRAIXND2D5SYBLQUOPDB4HZTV13TT22AGACD'

foursquare_client_secret = 'IHBS4VBHYWJL53NLIY2HSVI5A1144GJ3MDTYYY1KLKTMC4BV'

google_api_key = 'AIzaSyBz7r2Kz6x7wO1zV9_O5Rcxmt8NahJ6kos'

engine = create_engine('sqlite:///restaruants.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

@app.route('/restaurants', methods = ['GET', 'POST'])
def all_restaurants_handler():
  if request.method == 'GET':
  	# RETURN ALL RESTAURANTS IN DATABASE
  	restaurants = session.query(Restaurant).all()
  	return jsonify(restaurants = [i.serialize for i in restaurants])

  elif request.method == 'POST':
  	# MAKE A NEW RESTAURANT AND STORE IT IN DATABASE
    location = request.args.get('location', '')
    cuisine = request.args.get('cuisine', '')
    restaurant_info = findARestaurant(location, cuisine)
    restaurant = Restaurant(restaurant_name = restaurant_info['name'], restaurant_address = restaurant_info['address'], restaurant_image = restaurant_info['image'])
    session.add(restaurant)
    session.commit()
    return jsonify(restaurant = restaurant.serialize)
    
@app.route('/restaurants/<int:id>', methods = ['GET','PUT', 'DELETE'])
def restaurant_handler(id):
  restaurant = session.query(Restaurant).filter_by(id = id).one()
  if request.method == 'GET':
  	#RETURN A SPECIFIC RESTAURANT
  	return jsonify(restaurant = restaurant.serialize)
  elif request.method == 'PUT':
  	#UPDATE A SPECIFIC RESTAURANT
  	address = request.args.get('address')
  	image = request.args.get('image')
  	name = request.args.get('name')
  	if address != None:
  		restaurant.restaurant_address = address
  	if image != None:
  		restaurant.restaurant_image = image
  	if name != None:
  		restaurant.restaurant_name = name
  	session.commit()
  	return jsonify(restaurant = restaurant.serialize)

  elif request.method == 'DELETE':
  	#DELETE A SPECFIC RESTAURANT
  	session.delete(restaurant)
  	session.commit()
  	return "Restaurant Deleted"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5001)