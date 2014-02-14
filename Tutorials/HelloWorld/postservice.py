import datetime

from protorpc import message_types
from protorpc import remote
from protorpc import messages

import guestbook

class Note(messages.Message):

    text = messages.StringField(1, required=True)
    when = messages.IntegerField(2)

class PostService(remote.Service):

    #add remote dectorator
    @remote.method(Note, message_types.VoidMessage)
    def post_note(self, request):

        # if the note has a timestamp use it.
        if request.when is not None:
            when = datetime.datetime.utcfromtimestamp(request.when)

        else:
            when = datetime.datetime.now()


        note = guestbook.Greeting(parent=guestbook.guestbook_key(guestbook.DEFAULT_GUESTBOOK_NAME), content=request.text, date=when)
        note.put()
        return message_types.VoidMessage()
