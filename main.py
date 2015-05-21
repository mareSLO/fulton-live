#!/usr/bin/env python
import os
import jinja2
import webapp2
from google.appengine.api import users

from models import Sporocilo


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

        self.render_template("hello.html")


class PoslanoHandler(BaseHandler):
    def post(self):
        ime = self.request.get("ime")
        email = self.request.get("email")
        sporocilo = self.request.get("sporocilo")

        if ime == "":
            ime = "Neznan"

        if email == "":
            email = "Prazen"

        sporocilo1 = Sporocilo(ime=ime, email=email, sporocilo=sporocilo)
        sporocilo1.put()

        self.render_template("poslano.html")


class SeznamHandler(BaseHandler):
    def get(self):
        seznam = Sporocilo.query(Sporocilo.izbrisano == False).order(-Sporocilo.created).fetch()

        params = {"seznam": seznam}
        self.render_template("seznam.html", params)


class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}

        self.render_template("pos_sporocilo.html", params)


class UrediSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        params = {"sporocilo": sporocilo}

        self.render_template("uredi_sporocilo.html", params)

    def post(self, sporocilo_id):
        urejeno_ime = self.request.get("uredi_ime")
        urejen_email = self.request.get("uredi_email")
        urejeno_sporocilo = self.request.get("uredi_sporocilo")

        if urejeno_ime == "":
            urejeno_ime = "Neznan"

        if urejen_email == "":
            urejen_email = "Prazen"

        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.ime = urejeno_ime
        sporocilo.email = urejen_email
        sporocilo.sporocilo = urejeno_sporocilo
        sporocilo.put()

        return self.redirect_to("seznam")

class IzbrisiSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("izbrisi.html", params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        sporocilo.izbrisano = True
        sporocilo.put()
        return self.redirect_to("seznam")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/poslano', PoslanoHandler),
    webapp2.Route('/seznam', SeznamHandler, name="seznam"),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/uredi', UrediSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/izbrisi', IzbrisiSporociloHandler),
], debug=True)