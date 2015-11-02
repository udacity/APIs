from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    picture = Column(String)
    description = Column(String)
    price = Column(String)
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
        'name' : self.name,
        'picture' : self.picture,
        'price' : self.price,
        'description' : self.description
            }

engine = create_engine('sqlite:///bargainMart.db')
 

Base.metadata.create_all(engine)
    
