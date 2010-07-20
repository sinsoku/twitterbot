#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from omiaibot import OmiaiBot

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello, World')

def application():
    return webapp.WSGIApplication([('/omiaibot/', MainHandler),
                                   ('/omiaibot/task', OmiaiBot)],
                                   debug=True)

def main():
    util.run_wsgi_app(application())


if __name__ == '__main__':
    main()
