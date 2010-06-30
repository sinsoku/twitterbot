#!/usr/bin/env python
# -*- coding: utf-8 -*-
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import re
import tweepy

class Status(db.Model):
    id   = db.IntegerProperty()
    user = db.StringProperty()
    text = db.TextProperty()

class OmiaiBot(webapp.RequestHandler):
    def get(self):
        self.api = self.authTwitter()
        
        searchwords=[u'彼女ほしい OR 彼氏ほしい OR 彼女欲しい OR 彼氏欲しい']
        tweets = self.search(searchwords)
        tweets = self.filter(tweets)

        self.response.headers['Content-Type'] = 'text/html'
        for tweet in tweets:
            self.response.out.write('RT @' + tweet.from_user + ': ' + tweet.text + '<p>')
            self.post(tweet)
            self.put(tweet)

    def search(self, words):
        ''' wordsの語句を一つずつ検索し、検索結果を一つのリストにして返す。
        '''
        resultlist = []
        for word in words:
            resultlist += self.api.search(word.encode('utf-8'))

        # 重複要素を消去したリストを返す
        return sorted(set(resultlist), key=resultlist.index)

    def _isPosted(self, status):
        ''' DBにstatusのidが保存されていたらTrue, 保存されていなければFalseを返す。
        '''
        query = Status.all()
        query.filter('id =', status.id)
        return query.count() > 0

    def _isAgree(self, text):
        ''' text内の「彼女ほしい」に同意していればTrue, 同意していなければFalseを返す。
        '''
        doui = re.search(u'(ほしい|欲しい)', text)
        rtqt = re.search('(RT|QT)', text)
        return doui != None and rtqt != None and doui.span() < rtqt.span()

    def filter(self, status):
        ''' statusから条件に合わないステータスを消去する。
             * 前回までのcronで既にpostしているステータス
             * リンク(http)がついてるステータス
             * 同意するpostがRT/QTの前にないステータス
        '''
        filterdStatus = []

        for s in status:
            if (not self._isPosted(s)) and (not re.search('http://', s.text)) and (not re.search('(RT|QT)', s.text) or self._isAgree(s.text)):
                filterdStatus.append(s)

        return filterdStatus

    def post(self, status):
        ''' @userを_userに置換し、リプライが飛ばないように修正してからpostする。また、160字を超えていた場合はpostしない。
        '''
        text = 'RT @' + status.from_user + ': ' + status.text
        cnv_status = re.sub('@', '_', text)
        if len(cnv_status) < 160:
            self.api.update_status(cnv_status)

    def put(self, status):
        ''' postするstatusをデータストアに保存する
        '''
        s = Status()
        s.id = status.id
        s.user = status.from_user
        s.text = status.text
        s.put()

    def authTwitter(self):
        ''' Twitterの認証を行い、tweepy.APIを返す。
        '''
        ckey = ''
        csec = ''
        akey = ''
        asec = ''
        auth = tweepy.OAuthHandler(ckey, csec)
        auth.set_access_token(akey, asec)

        return tweepy.API(auth)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
