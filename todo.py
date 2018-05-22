from google.appengine.ext import ndb


class Task(ndb.Model):
    task_name = ndb.StringProperty()
    task_text = ndb.StringProperty()
    status = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)
