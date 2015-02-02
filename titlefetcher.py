#!/usr/bin/env python

import re
import Queue
import threading
import urllib2

class TitleFetcher(threading.Thread):
    def __init__(self):
        super(TitleFetcher, self).__init__()
        self.pattern = re.compile( '<title[^>]*>([^<]+)</title>' )
        self.queue = Queue.Queue()
        self.stopRequest = threading.Event()

    def setUsers( self, users ):
        self.users = users

    def fetch( self, url, recipients ):
        self.queue.put( ( url, recipients ) )

    def run( self ):
        while not self.stopRequest.isSet():
            try:
                _url, recipients = self.queue.get( True, 0.05 )
                try:
                    url = 'http://' + _url
                    response = urllib2.urlopen( url )
                    m = re.search( self.pattern, response.read() )
                    if m:
                        self.users.sendTitle( recipients, m.group( 1 ) )
                    else:
                        self.users.sendTitle( recipients, '~title not found~' )
                except:
                    self.users.sendTitle( recipients, '~server not found~' )
            except Queue.Empty:
                continue

    def join(self, timeout = None):
        self.stopRequest.set()
        super( TitleFetcher, self ).join( timeout )
