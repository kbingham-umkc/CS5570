import datetime

from protorpc import message_types
from protorpc import remote
from protorpc import messages
from google.appengine.ext import ndb

import mpg_db

class fillup(messages.Message):

    miles = messages.FloatField(1, required=True)
    gallons = messages.FloatField(2, required=True)
    id = messages.StringField(3)

class GetMPGRequest(messages.Message):
    limit = messages.IntegerField(1, default=20)

class MPGList(messages.Message):
    mpglist = messages.MessageField(fillup, 1, repeated=True)

class Deletemsg(messages.Message):
    id = messages.StringField(1, required=True)

class PostService(remote.Service):

    #add remote dectorator
    @remote.method(Deletemsg, MPGList)
    def delete_mpg(self, request):
        entkey = ndb.Key(urlsafe=request.id)
        entkey.delete()

        query = mpg_db.Miles_And_Fuel.query()
        mpglist = []
        for mpg in query.fetch(100):
            mpgItem = fillup(miles = mpg.miles, gallons=mpg.gallons, id=mpg.key.urlsafe())
            mpglist.append(mpgItem)
        
        return MPGList(mpglist=mpglist)


    #add remote dectorator
    @remote.method(fillup, MPGList)
    def post_mpg(self, request):

        note = mpg_db.Miles_And_Fuel(miles=request.miles, gallons=request.gallons)
        note.put()


        query = mpg_db.Miles_And_Fuel.query()
        mpglist = []
        for mpg in query.fetch(100):
            mpgItem = fillup(miles = mpg.miles, gallons=mpg.gallons, id=mpg.key.urlsafe())
            mpglist.append(mpgItem)
        
        mpglist.append(fillup(miles = request.miles, gallons = request.gallons))
        
        return MPGList(mpglist=mpglist)
    
    
    #Do a get on the site.
    @remote.method(GetMPGRequest, MPGList)
    def get_mpglist(self, request):
        
        query = mpg_db.Miles_And_Fuel.query()
        mpglist = []
        for mpg in query.fetch(100):
            mpgItem = fillup(miles = mpg.miles, gallons=mpg.gallons, id=mpg.key.urlsafe())
            mpglist.append(mpgItem)
            
        
        return MPGList(mpglist=mpglist)