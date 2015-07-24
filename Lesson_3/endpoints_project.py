# Create the appropriate app.route functions, test and see if they work, and paste your URI’s in the boxes below.f

#Make an app.route() decorator here
def PuppiesFunction():
  if request.method == 'GET'
  #Call the method to Get all of the puppies
  elif request.method == 'POST'
  #Call the method to make a new puppy
  
 
#Make another app.route() decorator here that takes in an integer id in the URI
def PuppiesFunction(id):
  if request.method == 'UPDATE'
  elif request.method == 'DELETE'


def GetAllPuppies():
  return "Getting All the puppies!"
  
def MakeANewPuppy():
  return "Creating A New Puppy!"

def UpdatePuppy(id):
  return "Updating a Puppy with id %s" % id

def DeletePuppy(id):
  return "Removing Puppy with id %s" % id
