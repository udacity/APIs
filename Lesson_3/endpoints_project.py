# Create the appropriate app.route functions, test and see if they work, and paste your URI’s in the boxes below.f

#Make an app.route() decorator here for when the client sends the URI "/puppies"
def puppiesFunction():
  return "Yes, puppies!"
  
 
#Make another app.route() decorator here that takes in an integer named 'id' for when the client visits a URI like "/puppies/5"
def puppiesFunction(id):
  return "This method will act on the puppy with id %s" % id

