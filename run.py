#!/usr/bin/env python

from server import Server
from config import loadConfig

def main():
    config = loadConfig( 'config.ini' )
    server = Server( config )
    server.run()

if __name__ == '__main__':
    main()

