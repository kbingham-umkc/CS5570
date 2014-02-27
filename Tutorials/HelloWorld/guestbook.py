import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import datetime


JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'], autoescape=True)


MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/sign?%s" method="post">
        <div><textarea name="content" rows="3" cols="60"></textarea></div>
        <div><input type="submit" value="Sign Guestbook"></div>
    </form>

    <hr>

    <form>Guestbook name:
        <input value="%s" name="guestbook_name">
        <input type="submit" value="switch">
    </form>

    <a href="%s">%s</a>
</body>
</html>
"""

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

class MainPage(webapp2.RequestHandler):

    def get(self):

        guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)

        #I don't do comments
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = "Logout"
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = "Login"

        #write submission
        template_values = {
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext, }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        


class Guestbook(webapp2.RequestHandler):

    def post(self):

        guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get("content")
        greeting.put()

        query_params= {'guestbook_name' : guestbook_name }
        self.redirect("/?" + urllib.urlencode(query_params))


class LoadTest(webapp2.RequestHandler):
    def get(self):
        template_values = dict()
        template = JINJA_ENVIRONMENT.get_template('LoadTest.html')
        self.response.write(template.render(template_values))

    def post(self):
        post_type = self.request.get("action").lower()
        create_duration = 0
        recordamount = 500
        delete_duration = 0
        deleteamount = 0
        error_str = ''
        if post_type == "createmultiplerecords":
            try:
                startTime = datetime.datetime.now()
                for x in range(recordamount):
                    newEntity = LoadTestEntity()
                    newEntity.key_value = x
                    newEntity.put()
                finishtime = datetime.datetime.now()
                create_duration = finishtime - startTime
            except Exception, e:
                error_str = repr(e)
        elif post_type == "deleteall":
            startTime = datetime.datetime.now()
            try:
                q = ndb.gql("SELECT __key__ FROM LoadTestEntity")
                deleteamount = q.count()
                while q.count() > 0:
                    ndb.delete_multi(q.fetch(200))
                    q = ndb.gql("SELECT __key__ FROM LoadTestEntity")
            except Exception, e:
                error_str = repr(e)
            finishtime = datetime.datetime.now()
            delete_duration = finishtime - startTime


        template_values = {
            'create_duration': "{} records in {} seconds".format(str(recordamount), str(create_duration)),
            'error' : error_str,
            'delete_duration': "{} records deleted in {} seconds".format(str(deleteamount), str(delete_duration))
        }
        template = JINJA_ENVIRONMENT.get_template('LoadTest.html')
        self.response.write(template.render(template_values))




application = webapp2.WSGIApplication(
    [
        ('/', MainPage),
        ('/sign', Guestbook),
        ('/loadtest', LoadTest)
    ], debug=True)
