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
        
        searchwords=[u'彼女ほしい OR 彼氏ほしい']
        tweets = self.search(searchwords)
        tweets = self.filter(tweets)
        self.saveTweets(tweets)

        self.response.headers['Content-Type'] = 'text/html'
        for tweet in tweets:
            self.response.out.write('[' + tweet.from_user + '] ')
            self.response.out.write(tweet.text + '<p>')
            self.retweet(tweet)

    def search(self, words):
        ''' wordsの語句を一つずつ検索し、検索結果を一つのリストにして返す。
        '''
        resultlist = []
        for word in words:
            resultlist += self.api.search(word.encode('utf-8'))

        # 重複要素を消去したリストを返す
        return sorted(set(resultlist), key=resultlist.index)

    def filter(self, status):
        ''' statusから条件に合わないステータスを消去する。
             * RT/QTしている人
              * 同意してる人は消去しない
              * 多段RT/QTは消去する
             * リンク(http)がついてる人
        '''
        query = Status.all()
        query.order('-id')
        db_latestobj = query.get()
        removeIndex = []

        # 一度postしたstatusは除去する
        for i in xrange(len(status)):
            # DBに保存（一度RT）されていたら除去する。
            if db_latestobj != None and status[i].id <= db_latestobj.id:
                removeIndex.append(i)
            elif re.search('http://', status[i].text):
                removeIndex.append(i)
            # 多段RTで4回以上RTされていたら除去する
            elif len(re.findall('(RT|QT)', status[i].text)) > 4:
                removeIndex.append(i)
            elif re.search('(RT|QT)', status[i].text) and re.search(u'(ほしい|欲しい)', status[i].text):
                doui = re.search(u'(ほしい|欲しい)', status[i].text).span()
                rtqt = re.search('(RT|QT)', status[i].text).span()
                # "ほしい"がRT/QTの前に無ければRT/QTしない
                if not doui < rtqt:
                    removeIndex.append(i)

            for j in xrange(len(status)):
                if status[i].id != status[j].id and (not j in removeIndex) and status[j].text.endswith(status[i].text):
                    removeIndex.append(i)

        filterdStatus = []
        for i in xrange(len(status)):
            if not i in removeIndex:
                filterdStatus.append(status[i])

        return filterdStatus

    def retweet(self, status):
        cnv_status = re.sub('@', ':', status.text)
        self.api.update_status(cnv_status)

    def saveTweets(self, status):
        ''' ReTweetするstatusをデータストアに保存する
        '''
        for tweet in status:
            s = Status()
            s.id = tweet.id
            s.user = tweet.from_user
            s.text = tweet.text
            s.put()

    def authTwitter(self):
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
