#< project.py >
#encoding=utf8
#author=maolion( maolion.j@gmail.com )
#date=2012/10/18
import os
import sys
import sublime
from Local import *


DEBUG = False

if DEBUG:   
    print ":: JProject on debug mode ::"

def MESSAGE( msg, c = True, prefix = "JProject: " ):
    if  not c: return None

    if DEBUG and len( msg ):
        print "%s%s" % ( prefix, msg )
        return None
    sublime.status_message( msg )

def init( module ):
    module       = sys.modules[ module ]
    module.PPATH = os.path.join( sublime.packages_path(), "JProject/" )
    module.CFG   = sublime.load_settings("JProject.sublime-settings")
    module.DLOC  = Local( os.path.join( module.PPATH, "local/" + module.CFG.get("default_language") ) )
    module.LOC   = Local( os.path.join( module.PPATH, "local/" + module.CFG.get("language") ), module.DLOC.copy()  )
    sys.modules[__name__].DEBUG = module.CFG.get("debug")

class XError( Exception ):pass


