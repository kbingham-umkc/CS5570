import datetime

from protorpc import message_types
from protorpc import remote
from protorpc import messages
from google.appengine.ext import ndb
from google.appengine.api import users

import mpg_db

class fillup(messages.Message):

    miles = messages.FloatField(1, required=True)
    gallons = messages.FloatField(2, required=True)
    id = messages.StringField(3)
    created = messages.StringField(4)

class GetMPGRequest(messages.Message):
    limit = messages.IntegerField(1, default=20)

class MPGList(messages.Message):
    mpglist = messages.MessageField(fillup, 1, repeated=True)
    totalmpg = messages.FloatField(2)

class Deletemsg(messages.Message):
    id = messages.StringField(1, required=True)

def FetchMPGList():
    mpglist = []
    
    
    query = mpg_db.Miles_And_Fuel.query(ancestor=mpg_db.user_key())
    for mpg in query.fetch(100):
        try:
            createdvalue = str(mpg.created)
        except:
            createdvalue = ""
        mpgItem = fillup(miles = mpg.miles, gallons=mpg.gallons, id=mpg.key.urlsafe(), created=createdvalue)
        mpglist.append(mpgItem)    
        
        
    return mpglist    

def TotalMPG(mpglist):
    miles = 0
    gallons = 0
    for mpg in mpglist:
        miles += mpg.miles
        gallons += mpg.gallons
    
    if gallons > 0:
        return miles / gallons
    return 0
    
class PostService(remote.Service):

    #add remote dectorator
    @remote.method(Deletemsg, MPGList)
    def delete_mpg(self, request):
        entkey = ndb.Key(urlsafe=request.id)
        entkey.delete()

        mpglist = FetchMPGList()
        return MPGList(mpglist=mpglist, totalmpg = TotalMPG(mpglist))


    #add remote dectorator
    @remote.method(fillup, MPGList)
    @ndb.transactional
    def post_mpg(self, request):

        note = mpg_db.Miles_And_Fuel(parent=mpg_db.user_key(), miles=request.miles, gallons=request.gallons)
        note.put()


        query = mpg_db.Miles_And_Fuel.query()
        mpglist = FetchMPGList()
       
        for mpg in mpglist:
            if mpg.id == note.key.urlsafe():
                break
        else:
            mpglist.append(fillup(miles = request.miles, gallons = request.gallons, id=note.key.urlsafe(), created=str(datetime.datetime.now())))
        
        mpg_db
        
        return MPGList(mpglist=mpglist, totalmpg = TotalMPG(mpglist))
    
    
    #Do a get on the site.
    @remote.method(GetMPGRequest, MPGList)
    def get_mpglist(self, request):
        
        mpglist = FetchMPGList()
        
        return MPGList(mpglist=mpglist, totalmpg = TotalMPG(mpglist))