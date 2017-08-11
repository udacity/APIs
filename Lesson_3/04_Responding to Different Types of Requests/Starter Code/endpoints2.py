from flask import Flask
app = Flask(__name__)
# Create the appropriate app.route functions, test and see if they work, and paste your URIs in the boxes below.

#Make an app.route() decorator here

def puppiesFunction():
  if request.method == 'GET':
  	#Call the method to Get all of the puppies
  	
  
  elif request.method == 'POST':
  	#Call the method to make a new puppy
  
  
 
#Make another app.route() decorator here that takes in an integer id in the 

def puppiesFunctionId(id):
  if request.method == 'GET':
  	#Call the method to get a specific puppy based on their id
  	
  if request.method == 'PUT':
  	#Call the method to update a puppy
  	
  elif request.method == 'DELETE':
  	#Call the method to remove a puppy
  	


def getAllPuppies():
  return "Getting All the puppies!"
  
def makeANewPuppy():
  return "Creating A New Puppy!"

def getPuppy(id):
	return "Getting Puppy with id %s" % id
	
def updatePuppy(id):
  return "Updating a Puppy with id %s" % id

def deletePuppy(id):
  return "Removing Puppy with id %s" % id
