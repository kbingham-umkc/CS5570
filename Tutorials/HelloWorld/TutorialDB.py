#region -- import declarations --
from google.appengine.ext import ndb

#endregion


__author__ = 'KBingham'

# Provide the classes and Database Entity Definitions.

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Construct datastore key for Guestbook entity"""
    return ndb.Key('Guestbook', guestbook_name)


class Greeting(ndb.Model):
    """Models and individual guestbook entry"""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class LoadTestEntity(ndb.Model):
    key_value = ndb.IntegerProperty(indexed=True)
