
# region -- imports --

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import datetime

import TutorialDB as tdb

# endregion


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


class MainPage(webapp2.RequestHandler):

    def get(self):

        guestbook_name = self.request.get('guestbook_name', tdb.DEFAULT_GUESTBOOK_NAME)

        #I don't do comments
        greetings_query = tdb.Greeting.query(
            ancestor=tdb.guestbook_key(guestbook_name)).order(-tdb.Greeting.date)
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

        guestbook_name = self.request.get('guestbook_name', tdb.DEFAULT_GUESTBOOK_NAME)
        greeting = tdb.Greeting(parent=tdb.guestbook_key(guestbook_name))

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
        startTime = datetime.datetime.now()
        post_type = self.request.get("action").lower()
        records_int = 0
        error_str = ''
        action_str = ""
        try:
            if post_type == "createmultiplerecords":
                action_str = "added"
                records_int = 500
                for x in range(records_int):
                    newEntity = tdb.LoadTestEntity()
                    newEntity.key_value = x
                    newEntity.put()
            elif post_type == "deleteall":
                action_str = "deleted"
                q = ndb.gql("SELECT __key__ FROM LoadTestEntity")
                records_int = q.count()
                while q.count() > 0:
                    ndb.delete_multi(q.fetch(200))
                    q = ndb.gql("SELECT __key__ FROM LoadTestEntity")
        except Exception, e:
            error_str = repr(e)

        finishtime = datetime.datetime.now()
        duration = finishtime - startTime

        template_values = {
            'action_message': "{} records {} in {} seconds".format(str(records_int), action_str, str(duration)),
            'error' : error_str
        }
        template = JINJA_ENVIRONMENT.get_template('LoadTest.html')
        self.response.write(template.render(template_values))




application = webapp2.WSGIApplication(
    [
        ('/', MainPage),
        ('/sign', Guestbook),
        ('/loadtest', LoadTest)
    ], debug=True)
