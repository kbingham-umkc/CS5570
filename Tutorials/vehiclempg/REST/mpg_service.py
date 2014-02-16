import datetime

from protorpc import message_types
from protorpc import remote
from protorpc import messages

import mpg_db

class fillup(messages.Message):

    miles = messages.FloatField(1, required=True)
    gallons = messages.FloatField(2, required=True)

class GetMPGRequest(messages.Message):
    limit = messages.IntegerField(1, default=20)

class MPGList(messages.Message):
    mpglist = messages.MessageField(fillup, 1, repeated=True)

class PostService(remote.Service):

    #add remote dectorator
    @remote.method(fillup, message_types.VoidMessage)
    def post_mpg(self, request):

        note = mpg_db.Miles_And_Fuel(miles=request.miles, gallons=request.gallons)
        note.put()
        return message_types.VoidMessage()

    #Do a get on the site.
    @remote.method(GetMPGRequest, MPGList)
    def get_mpglist(self, request):
        
        query = mpg_db.Miles_And_Fuel.query()
        mpglist = []
        for mpg in query.fetch(10):
            mpgItem = fillup(miles = mpg.miles, gallons=mpg.gallons)
            mpglist.append(mpgItem)
            
        
        return MPGList(mpglist=mpglist)