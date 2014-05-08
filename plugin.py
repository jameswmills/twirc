###
# Copyright (c) 2014, James W. Mills
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.log as log
import oauth2 as oauth
import json
import dateutil.tz
from datetime import datetime

class Twirc(callbacks.Plugin):
    """Add the help for "@plugin help Twirc" here
    This should describe *how* to use this plugin."""
    def __init__(self, irc):
        self.__parent = super(Twirc, self)
        self.__parent.__init__(irc)
        self.access_key = self.registryValue('accessKey') 
        self.access_secret = self.registryValue('accessSecret') 
        self.consumer_key = self.registryValue('consumerKey') 
        self.consumer_secret = self.registryValue('consumerSecret') 
        self.http_method = "GET"
        self.post_body = ""
        self.http_headers = None
        self.client = self.get_oauth_client()

    def get_oauth_client(self):
      consumer = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)
      token = oauth.Token(key=self.access_key, secret=self.access_secret)
      client = oauth.Client(consumer, token)
      return client

    def oauth_req(self, url):
      resp, content = self.client.request(
        url,
        method=self.http_method,
        body=self.post_body,
        headers=self.http_headers
      )
      return content

    def pretty_local_time(self, timestring):
      timestring = timestring.replace('+0000', 'UTC')
      tweet_time = datetime.strptime(timestring, '%a %b %d %H:%M:%S %Z %Y')
      tweet_time = tweet_time.replace(tzinfo=dateutil.tz.tzutc())
      return tweet_time.astimezone(dateutil.tz.tzlocal()).strftime("%a %b %d %H:%M:%S %Z %Y")

    def get_trending(self, count):
      answer = []
      trending = self.oauth_req('https://api.twitter.com/1.1/trends/place.json?id=%s' % self.registryValue('trendingID'))
      response = json.loads(trending)
      for resp in response[0]['trends']:
        answer.append("%s (%s)" % (resp['name'], resp['url']))
      return answer[:count]

    def get_last_tweet(self, user, count=1):
      answer = []
      last_tweet = self.oauth_req('https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s&count=%d' % (user, count))
      response = json.loads(last_tweet)
      if not response or isinstance(response, dict):
        if isinstance(response, dict) and 'errors' in response.keys():
          answer.append("ERROR: %s -- Please configure Twirc with the proper access and consumer keys/secrets.  These can be obtained by getting API keys from https://apps.twitter.com" % response['errors'][0]['message'])
        else:
          answer.append("Wha?  I have no tweets from %s..." % user)
      else:
        for resp in response:
          timestamp = self.pretty_local_time(resp['created_at'])
          answer.append("%s [%s] (%s)" % (resp['text'], resp['user']['screen_name'], timestamp))
      return answer

    def send_msg(self, irc, answer, user=None):
      if not user:
        user = "trending"
      for tweet in answer:
        try:
          irc.reply(tweet.encode('utf-8'), prefixNick=False)
        except:
          irc.reply("""The latest tweet from "%s" has some weird characters that I cannot parse.  Sorry!""" % user, prefixNick=False)

    def latest(self, irc, msg, tokens, user):
      """<user>

      Print the "latest" tweet from <user>, or from the "defaultUser" config option if <user> is not provided.
      """
      channel = msg.args[0]
      if not user:
        user = self.registryValue('defaultUser')
      if not irc.isChannel(channel):
        return
      answer = self.get_last_tweet(user)
      self.send_msg(irc, answer, user)

    latest = wrap(latest, [optional('somethingWithoutSpaces')])

    def last(self, irc, msg, tokens, count, user):
      """<count> <user>

      Print the "last" <count> tweets from <user>, or from the "defaultUser" config option if <user> is not provided.
      """
      channel = msg.args[0]
      if not user:
        user = self.registryValue('defaultUser')
      if not irc.isChannel(channel):
        return
      answer = self.get_last_tweet(user, count)
      self.send_msg(irc, answer, user)

    last = wrap(last, [('int', 'tweet count'), optional('somethingWithoutSpaces')])


    def trending(self, irc, msg, tokens, count):
      """

      Get the top <count> worldwide trending tweets.  <count> is optional, defaults to 5, and has a max of 10
      """
      if not count:
        count = self.registryValue('trendingResults')
      answer = self.get_trending(count)
      self.send_msg(irc, answer)
    trending = wrap(trending, [optional('int')])
Class = Twirc


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
