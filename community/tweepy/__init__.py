# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '2.0'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from community.tweepy.models import Status, User, DirectMessage, Friendship, SavedSearch, SearchResult, ModelFactory, Category
from community.tweepy.error import TweepError
from community.tweepy.api import API
from community.tweepy.cache import Cache, MemoryCache, FileCache
from community.tweepy.auth import BasicAuthHandler, OAuthHandler
from community.tweepy.streaming import Stream, StreamListener
from community.tweepy.cursor import Cursor

# Global, unauthenticated instance of API
api = API()


def debug(enable=True, level=1):
    import httplib

    httplib.HTTPConnection.debuglevel = level

