#!/usr/bin/env python
import os
import jinja2
import webapp2
from todo import Task

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
        return self.render_template("index.html")

    def post(self):
        task_name = self.request.get("task_name")
        task_text = self.request.get("task_text")
        done_check = self.request.get("done")

        if done_check:
            todo = Task(task_name=task_name, task_text=task_text, status=True)
            todo.put()
        else:
            todo = Task(task_name=task_name, task_text=task_text, status=False)
            todo.put()

        return self.render_template("index.html")


class AllTaskHandler(BaseHandler):
    def get(self):
        all_tasks = Task.query(Task.deleted == False).fetch()
        params = {"all_tasks": all_tasks}
        return self.render_template("opravila.html", params=params)

    def post(self, opravilo_id):
        task = Task.get_by_id(int(opravilo_id))
        text = self.request.get("new_text")
        task.task_text = text
        task.put()

        params = {"new_text": task}

        return self.render_template("opravila.html", params=params)


class DeleteTaskHandler(BaseHandler):
    def post(self, opravilo_id):
        message_model = Task.get_by_id(int(opravilo_id))
        message_model.key.delete()
        message_model.deleted = True
        message_model.put()
        return self.render_template("opravila.html")


class DeletedTasksHandler(BaseHandler):
    def get(self):
        deleted_tasks = Task.query(Task.deleted == True).fetch()
        params = {"deleted_tasks": deleted_tasks}
        return self.render_template("izbrisana_opravila.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/opravila', AllTaskHandler),
    webapp2.Route('/opravila/<opravilo_id:\d+>', AllTaskHandler),
    webapp2.Route('/izbris/<opravilo_id:\d+>', DeleteTaskHandler),
    webapp2.Route('/izbrisana_opravila', DeletedTasksHandler),
], debug=True)
