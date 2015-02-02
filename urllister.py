#!/usr/bin/env python

import re

class URLLister( object ):
    def __init__( self ):
        self.pattern = re.compile( 'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' )

    def get( self, text ):
        return re.findall( self.pattern, text )
