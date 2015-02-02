#!/usr/bin/env python

import asyncore
import socket
import threading

from users import Users
from titlefetcher import TitleFetcher
from log import log

class ClientHandler( asyncore.dispatcher ):

    def __init__( self, socket, config ):
        asyncore.dispatcher.__init__( self, socket )
        self.name = None
        self.mutex = threading.Lock()
        self.buffer = ''
        self.config = config

    def setUsers( self, users ):
        self.users = users

    def welcome( self ):
        self.write_data( 'ChatServ v1.0\n\n{0}\n\nInsert your name: '.format( self.config.welcome ) )

    def handle_read( self ):
        data = self.recv( 8192 )

        if data:
            if self.name is None:
                list = data.split( None, 1 )
                if len( list ) == 0:
                    return
                elif len( list ) == 1:
                    self.name = list[ 0 ]
                    data = ''
                else:
                    self.name = list[ 0 ]
                    data = len[ 1 ]
                try:
                    self.users.addUser( self.name, self )
                except UserMap.Error as ex:
                    self.name = None
                    self._exitConnection( str( ex ) )
                    return

        if data:
            self.users.message( self.name, data )

    def write_data( self, data ):
        self.mutex.acquire()
        self.buffer += data
        self.mutex.release()

    def handle_close( self ):
        if self.name is not None:
            self.users.removeUser( self.name )
        self.disconnect()

    def disconnect( self ):
        while self.writable():
            self.handle_write()
        self.close()

    def handle_write( self ):
        self.mutex.acquire()
        sent = self.send( self.buffer )
        self.buffer = self.buffer[ sent: ]
        self.mutex.release()

    def writable( self ):
        try:
            self.mutex.acquire()
            return len( self.buffer ) > 0
        finally:
            self.mutex.release()

    def _exitConnection( self, reason ):
        msg = '[SRV]: Connection refused: {0}\n'.format( reason )
        self.write_data( msg )
        log( msg )
        self.handle_close()

class ConnectionDispatcher( asyncore.dispatcher ):

    def __init__( self, config ):
        asyncore.dispatcher.__init__( self )
        self.create_socket( socket.AF_INET, socket.SOCK_STREAM )
        self.set_reuse_addr()
        self.bind( (config.host, config.port) )
        self.listen( 5 )
        self.config = config

        log( 'Server is running at {0}:{1}\n'.format( config.host, config.port ) )
        log( 'Maximum number of users is {0}\n'.format( config.limit ) )

    def setUsers( self, users ):
        self.users = users

    def handle_accept( self ):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            log( '[SRV]: Incoming connection from {0}\n'.format( repr( addr ) ) )
            handler = ClientHandler( sock, self.config )
            handler.setUsers( self.users )
            handler.welcome()

class Server( object ):

    def __init__( self, config ):
        self.config = config

    def run( self ):
        users = Users( self.config.limit )
        titleFetcher = TitleFetcher()

        users.setFetcher( titleFetcher )
        titleFetcher.setUsers( users )
        
        try:
            server = ConnectionDispatcher( self.config )
        except:
            log( 'Cannot start server: {0}:{1} is already in use.\n'.format( self.config.host, self.config.port ) )
            return
        server.setUsers( users )

        titleFetcher.start()

        try:
            asyncore.loop( 0.1 )
        except KeyboardInterrupt:
            users.message( '[SRV]', 'server is shutting down\n' )
            users.report = False

        titleFetcher.join()
        users.disconnectAll()
