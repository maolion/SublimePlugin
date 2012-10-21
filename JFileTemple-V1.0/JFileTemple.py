#< JFileTemple.py >
#encoding=utf8
#author=maolion( maolion.j@gmail.com )
#date=2012/10/21

import os
import sys
import sublime
from StringTemple import *
from Local import *

def moduleInit( module ):
    module            = sys.modules[ module ]
    module.PPATH      = PPATH
    module.DLOC       = Local( os.path.join( PPATH, "local/" + CFG.get("default_language") ) )
    module.LOC        = Local( os.path.join( PPATH, "local/" + CFG.get("language") ), module.DLOC.copy()  )
    module.DEBUG      = CFG.get("debug")
    module.CFG        = JFileTemple.CFG
    module.message    = message
    JFileTemple.DEBUG = module.DEBUG

    CFG.erase( "temple_dir" )
    CFG.set( 
        "temple_dir", 
        altsep( StringTemple( CFG.get( "temple_dir" ), { "plugin_path" : PPATH }  ).parse() )
    )
    
def message( msg, c = True, prefix = __name__ + ": " ):
    if  not c: return None
    msg = "%s%s" % ( prefix, msg )
    if DEBUG and len( msg ):
        print msg
        return None
    sublime.status_message( msg )

def altsep( path ):
    return path.replace( os.sep, os.altsep )

class XError( Exception ):pass


DEBUG       = False
PNAME       = __name__
PPATH       = altsep( os.path.join( sublime.packages_path(), PNAME ) )
CFG         = sublime.load_settings( PNAME + ".sublime-settings" )
JFileTemple = sys.modules[ __name__ ]

