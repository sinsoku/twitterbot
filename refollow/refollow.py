#!/usr/env/bin python
# -*- encoding:utf-8 -*-
import twitter

# twitter.Api.__init__ method for override.
def twitter_api_init_gae(self,
                       username=None,
                       password=None,
                       input_encoding=None,
                       request_headers=None):
   import urllib2
   from twitter import Api
   self._cache = None

   self._urllib = urllib2
   self._cache_timeout =  Api.DEFAULT_CACHE_TIMEOUT
   self._InitializeRequestHeaders(request_headers)
   self._InitializeUserAgent()
   self._InitializeDefaultParameters()
   self._input_encoding = input_encoding
   self.SetCredentials(username, password)

# overriding API __init__
twitter.Api.__init__ = twitter_api_init_gae

# AutoRefollow main
USER = '<username>'
PASS = '<password>'

api = twitter.Api(username = USER, password = PASS)
tl = api.GetFriendsTimeline() 

for s in tl:
    print "[%10s] %s" % (s.user.screen_name.encode('utf-8'), s.text.encode('utf-8'))
