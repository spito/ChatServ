#!/usr/bin/env python

import threading
from userlister import UserLister
from urllister import URLLister
from log import log

class Users( object ):

    class Error( Exception ):
        def __init__( self, value ):
            self.value = value
        def __str__( self ):
            return repr( self.value )

    def __init__( self, limit ):
        self.mutex = threading.Lock()
        self.map = dict()
        self.limit = limit
        self.userLister = UserLister()
        self.urlLister = URLLister()
        self.titleFetcher = None
        self.report = True

    def setFetcher( self, titleFetcher ):
        self.titleFetcher = titleFetcher

    def users( self ):
        try:
            self.mutex.acquire()
            return self.map.keys()
        finally:
            self.mutex.release()

    def disconnectAll( self ):
        self.mutex.acquire()

        for connector in self.map.itervalues():
            connector.disconnect()

        self.mutex.release()

    def addUser( self, name, handler ):
        self.mutex.acquire()

        try:
            if len( self.map ) == self.limit:
                raise UserMap.Error( 'maximum connections limit reached' )
            if name in self.map or name in [ '[SRV]', '[TitleFetcher]' ]:
                raise UserMap.Error( 'chosen name is already used' )

            self.map[ name ] = handler
            if self.report:
                self._messageAll( '[SRV]', [ name ], 'User {0} has joined.\n'.format( name ) )
        finally:
            self.mutex.release()

    def removeUser( self, name ):
        self.mutex.acquire()
        if name in self.map:
            del self.map[ name ]
            if self.report:
                self._messageAll( '[SRV]', [ name ], 'User {0} has quit.\n'.format( name ) )
        self.mutex.release()

    def message( self, name, text ):
        self.mutex.acquire()
        users = self.userLister.get( text )
        if len( users ) > 0:
            self._messageUsers( name, users, text )
            users.append( name )
        else:
            self._messageAll( name, [ name ], text )
            users = self.map.keys()

        if self.titleFetcher is not None:
            for url in self.urlLister.get( text ):
                self.titleFetcher.fetch( url, users )
        self.mutex.release()

    def sendTitle( self, recipients, link ):
        self.mutex.acquire()
        msg = '[TitleFetcher]: {0}\n'.format( link )
        log( msg )
        for r in recipients:
            if self._canIgnore( r ):
                continue
            self.map[ r ].write_data( msg )

        self.mutex.release()

    def _messageAll( self, who, exclude, text ):
        msg = '{0}: {1}'.format( who, text )
        log( msg )
        for _n, item in self.map.iteritems():
            if _n in exclude:
                continue
            item.write_data( msg )
        
    def _messageUsers( self, who, recipients, text ):
        msg = '{0}: {1}'.format( who, text )
        log( msg )
        for r in recipients:
            if r == who:
                continue
            if self._canIgnore( r ):
                continue
            self.map[ r ].write_data( msg )

    def _canIgnore( self, name ):
        name = name.lower()
        for key in self.map.keys():
            if key.lower() == name.lower():
                return False
        return True
