#!/urs/bin/env python

from ConfigParser import SafeConfigParser
from optparse import OptionParser

def _loadIni( path ):
    config = SafeConfigParser()
    config.read( path )

    result = dict()
    result[ 'host' ] = config.get( 'server', 'host' )
    result[ 'port' ] = config.getint( 'server', 'port' )
    result[ 'limit' ] = config.getint( 'server', 'limit' )
    result[ 'welcome' ] = config.get( 'text', 'welcome' )

    return result    

def _loadOptions():
    parser = OptionParser("%prog [-s HOST] [-p PORT] [-l LIMIT] [-w WELCOME]") # 1st argument is usage, %prog is replaced with sys.argv[0]
    parser.add_option(
        "-s", "--server",
        dest = "host",
        type = "string",
        action = "store",
        help = "IRC server address",
    )
    parser.add_option(
        "-p", "--port",
        dest = "port",
        type = "int",
        action = "store",
        help = "IRC server port",
    )
    parser.add_option(
        "-l", "--limit",
        dest = "limit",
        type = "int",
        action = "store",
        help = "maximum allowed connected users",
    )
    parser.add_option(
        "-w", "--welcome",
        dest = "welcome",
        type = "string",
        action = "store",
        help = "welcome message",
    )
    options, _ = parser.parse_args()
    result = dict()
    for k, v in vars( options ).items():
        if v is not None:
            result[ k ] = v
    return result

class Config( object ):
    host = 'localhost'
    port = 8080
    limit = 5
    welcome = 'Hello incoming user!'
    
    def merge( self, d ):
        if 'host' in d:
            self.host = d[ 'host' ]
        if 'port' in d:
            self.port = d[ 'port' ]
        if 'limit' in d:
            self.limit = d[ 'limit' ]
        if 'welcome' in d:
            self.welcome = d[ 'welcome' ]


def loadConfig( path ):
    d = _loadIni( path )
    d.update( _loadOptions() )

    config = Config()
    config.merge( d )
    return config
