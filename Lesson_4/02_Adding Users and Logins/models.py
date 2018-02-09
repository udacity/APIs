"""Create a users database containing a User model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


class User(Base):
    """Define the User model for the database."""

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))

    def hash_password(self, password):
        """Store a hash of a plain user password string in the User table.

        Called when:
        - a new user is registering with the server
        - a user changes their password

        Argument:
        password (string): plain password
        """
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """Return true if a password is correct, false if it's not.

        Called when a user provides credentials that they need to be validated

        Argument:
        password (string): plain password
        """
        return pwd_context.verify(password, self.password_hash)


engine = create_engine('sqlite:///users.db')


Base.metadata.create_all(engine)
