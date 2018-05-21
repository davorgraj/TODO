#!/usr/bin/env python
import os
import jinja2
import webapp2
from user import User

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")

    def post(self):
        name = self.request.get("name")
        email = self.request.get("email")
        message = self.request.get("message")

        if not name:
            name = "Neznanec"

        cb_object = User(name=name, email=email, text=message.replace("<script>", ""))
        cb_object.put()

        return self.render_template("hello.html")


class AllUserMessagesHandler(BaseHandler):
    def get(self):
        all_user_messages = User.query(User.deleted == False).fetch()
        params = {"all_user_messages": all_user_messages}
        return self.render_template("prejeta_sporocila.html", params=params)

    def post(self, sporocilo_id):
        new_message = User.get_by_id(int(sporocilo_id))
        message = self.request.get("message")
        new_message.text = message
        new_message.put()

        params = {"message": new_message}

        return self.render_template("prejeta_sporocila.html", params=params)


class MessageDeleteHandler(BaseHandler):
    def post(self, sporocilo_id):
        message_model = User.get_by_id(int(sporocilo_id))
        message_model.key.delete()
        message_model.deleted = True
        message_model.put()
        return self.render_template("prejeta_sporocila.html")


class AllDeletedHandler(BaseHandler):
    def get(self):
        deleted_messages = User.query(User.deleted == True).fetch()
        params = {"deleted_messages": deleted_messages}
        return self.render_template("izbrisana_sporocila.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/prejeta_sporocila', AllUserMessagesHandler),
    webapp2.Route('/prejeta_sporocila/<sporocilo_id:\d+>', AllUserMessagesHandler),
    webapp2.Route('/izbris_sporocila/<sporocilo_id:\d+>', MessageDeleteHandler),
    webapp2.Route('/izbrisana_sporocila', AllDeletedHandler),
], debug=True)
