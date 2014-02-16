import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

def user_key(user_id=""):
    if user_id == "":
        if users.get_current_user():
            user_id = users.get_current_user().user_id()
        else:
            user_id = "none"
    return ndb.Key('User', user_id)

class Miles_And_Fuel(ndb.Model):
    """Models and individual guestbook entry"""
    miles = ndb.FloatProperty(indexed=False)
    gallons = ndb.FloatProperty(indexed=False)
    created = ndb.DateTimeProperty(indexed=True, auto_now_add=True)

class UserTotal(ndb.Model):
    user_id = ndb.StringProperty(indexed=True)
    mpg = ndb.FloatProperty(indexed=False)