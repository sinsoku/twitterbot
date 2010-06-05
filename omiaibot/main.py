#!/usr/bin/env python
# -*- coding:utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import tweepy

class MainHandler(webapp.RequestHandler):
    def get(self):
        ckey = ''
        csec = ''
        akey = ''
        asec = ''
        auth = tweepy.OAuthHandler(ckey, csec)
        auth.set_access_token(akey, asec)
        api = tweepy.API(auth)

        self.response.headers['Content-Type'] = 'text/html'
        tweets = api.search('îﬁèóÇŸÇµÇ¢')
        for tweet in tweets:
            self.response.out.write('[' + tweet.from_user + '] ')
            self.response.out.write(tweet.text + '<p>')

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
