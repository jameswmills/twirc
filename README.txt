Twirc - A simple supybot Twitter interface

Usage

This plugin supports the following commands:

latest <user>
This command will display the last tweet from <user>.  If <user> is
not specified, the config value "defaultUser" will be used.

last <number> <user>
This command will display the last <number> of tweets from <user>.  If
<user> is not specified, the config value "defaultUser" will be used.

trending <number>
This command will display <number> of tweets currently trending.  If
<number> is not specified, the config value "trendingResults" will be
used.

The trends are taken from the region specified in the config value
"trendingID".  This is a Yahoo "Where On Earth" Identifier (WOEID).  You
can use sites like http://woeid.rosselliot.co.nz/ to fine-tune the
trend results.  The default trendingID is the United States.  FOr
"Global" results, use trendingID 1.

Configuration

IMPORTANT:  After intstalling Twirc, you *must* set the
"accessSecret", "accessKey", "consumerSecret", and "consumerKey"
configuration values and reload the Twirc plugin!

These keys can be obtained by logging into https://apps.twitter.com
and creating a Twitter app and generating API keys.  It takes about
three minutes ;)

KNOWN ISSUES:

* Special character handling - Right now an exception is occasionally
  thrown when irc.reply() is handling some UTF-8 strings.  I'm
  currently simply catching that error and spitting out an "I cannot
  handle this" message.

I'm sure there are plenty of *unknown* issues, but I wanted to get
this out here in case there was interest.
