import httplib2


#TEST ONE -- CREATE NEW RESTAURANTS
try:
	url = ('http://localhost:5000/restaurants?location=La+Paz+Bolivia&cuisine=Sushi')
	h = httplib2.Http()
    result = json.loads(h.request(url,'POST')[1])
    print result

    url = ('http://localhost:5000/restaurants?location=Denver+Colorado&cuisine=Thai')
	h = httplib2.Http()
    result = json.loads(h.request(url,'POST')[1])
 	print result

    url = ('http://localhost:5000/restaurants?location=Prague+Czech+Republic&cuisine=Hamburgers')
	h = httplib2.Http()
    result = json.loads(h.request(url,'POST')[1])
    print result

    url = ('http://localhost:5000/restaurants?location=Cairo+Egypt&cuisine=Sandwiches')
	h = httplib2.Http()
    result = json.loads(h.request(url,'POST')[1])
    print result

    url = ('http://localhost:5000/restaurants?location=Accra+Ghana&cuisine=Chinese')
	h = httplib2.Http()
    result = json.loads(h.request(url,'POST')[1])
    print result

except Exception, e:
	raise
else:
	print "Test 1 Passed Successfully"
	pass
finally:
	break


#TEST TWO -- READ ALL RESTAURANTS
try:
	url = ('localhost:5000/restaurants')
	pass
except Exception, e:
	raise
else:
	print "Test 2 Passed Successfully"
	pass
finally:
	pass

#TEST THREE -- READ A SPECIFIC RESTAURANT
try:
	url = ('localhost:5000/restaurants/2')
	pass
except Exception, e:
	raise
else:
	print "Test 3 Passed Successfully"
	pass
finally:
	pass


#TEST FOUR -- UPDATE A RESTAURANT

#TEST FIVE -- DELETE A RESTAURANT