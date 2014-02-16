import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb



class Miles_And_Fuel(ndb.Model):
    """Models and individual guestbook entry"""
    miles = ndb.FloatProperty(indexed=False)
    gallons = ndb.FloatProperty(indexed=False)
