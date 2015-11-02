from redis import Redis
import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify 
from models import Base, Item


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import json

engine = create_engine('sqlite:///bargainMart.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)




app = Flask(__name__)
redis = Redis()





class RateLimit(object):
    expiration_window = 10

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = redis.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)

def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)

def on_over_limit(limit):
    return (jsonify({'data':'You hit the rate limit','error':'429'}),429)

def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator



@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response

@app.route('/catalog')
@ratelimit(limit=30, per=60 * 1)
def getCatalog():
    items = session.query(Item).all()

    #Populate an empty database
    if items == []:
        item1 = Item(name="Pineapple", price="$2.50", picture="https://upload.wikimedia.org/wikipedia/commons/c/cb/Pineapple_and_cross_section.jpg", description="Organically Grown in Hawai'i")
        session.add(item1)
        item2 = Item(name="Carrots", price = "$1.99", picture = "http://media.mercola.com/assets/images/food-facts/carrot-fb.jpg", description = "High in Vitamin A")
        session.add(item2)
        item3 = Item(name="Aluminum Foil", price="$3.50", picture = "http://images.wisegeek.com/aluminum-foil.jpg", description = "300 feet long")
        session.add(item3)
        item4 = Item(name="Eggs", price = "$2.00", picture = "http://whatsyourdeal.com/grocery-coupons/wp-content/uploads/2015/01/eggs.png", description = "Farm Fresh Organic Eggs")
        session.add(item4)
        item5 = Item(name="Bananas", price = "$2.15", picture = "http://dreamatico.com/data_images/banana/banana-3.jpg", description="Fresh, delicious, and full of potassium")
        session.add(item5)
        session.commit()
        items = session.query(Item).all()
    return jsonify(catalog = [i.serialize for i in items])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
     

	
   