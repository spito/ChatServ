#!/usr/bin/env python

import re

class UserLister( object ):
    def __init__( self ):
        self.pattern = re.compile( '@([0-9a-zA-Z_]+)' )

    def get( self, text ):
        return re.findall( self.pattern, text )