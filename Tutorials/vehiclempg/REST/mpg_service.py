import datetime

from protorpc import message_types
from protorpc import remote
from protorpc import messages

import mpg_db

class fillup(messages.Message):

    miles = messages.FloatField(1, required=True)
    gallons = messages.FloatField(2, required=True)

class PostService(remote.Service):

    #add remote dectorator
    @remote.method(fillup, message_types.VoidMessage)
    def post_mpg(self, request):

        note = mpg_db.Miles_And_Fuel(miles=request.miles, gallons=request.gallons)
        note.put()
        return message_types.VoidMessage()
