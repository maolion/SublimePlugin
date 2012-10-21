#< JProjectImportTemple.py >
#encoding=utf8
#author=(  )
#date=2012/10/21

import os
import sublime, sublime_plugin
import JProject
import shutil

from JProject import message, altsep, XError
from Queue import *

class JProjectImportTemple( sublime_plugin.WindowCommand ):

    def run(self):
        JProject.moduleInit( __name__ )
        self.__templist = []
        try:
            self.__getTempleList()
        except Exception, e:
            sublime.error_message( LOC["GET_TEMPLE_LIST_FAIL"] )
            message( "REAL_ERROR: " + str(e), c = DEBUG )

        self.__showTempleList()

    def __getTempleList( self ):
        directory = CFG.get( "temple_dir" )
        items = os.listdir( directory )
        self.__templist = []
        for item in items:
            path = altsep( os.path.join( directory, item ) )
            if os.path.isdir( path ):
                self.__templist.append( path )
    
    def __showTempleList( self ):
        self.__templist.sort(key=lambda path: os.path.basename( path.lower() ) )
        chooslist = []
        for item in self.__templist:
            chooslist.append( os.path.basename( item ) )
        sublime.active_window().show_quick_panel( chooslist, self.__onInputDone )  

    def __onInputDone( self, index ):
        if index == -1: return None
        override = sublime.ok_cancel_dialog( LOC["CONFIRM_IMPORT_OVERRIDE"] )
        try:
            self.__importTemple( self.__templist[index], self.window.folders()[0], override )
        except Exception, e:
            print e
            sublime.error_message( LOC["IMPORT_TEMPLE_FAIL"] )
            message( "REAL_ERROR: " + str(e), c = DEBUG )

    def __importTemple( self, temple, project, override = False ):
        fqueue = Queue( 0, [ temple ] )
        temple = altsep( temple )
        project= altsep( project )
        while True:
            if fqueue.empty(): break
            src_dir = altsep( fqueue.get() )
            des_dir = src_dir.replace( temple, project )
            items = os.listdir( src_dir )
            message( "directory:" + src_dir, c = DEBUG )
            for item in items:
                src = os.path.join( src_dir, item )
                des = os.path.join( des_dir, item )
                message( "file: " + src, c = DEBUG  )
                if os.path.isdir( src ):
                    if not os.path.isdir( des ):
                        os.makedirs( des )
                        message( "create directory: " + des, c = DEBUG  )
                    fqueue.put( src )
                else:
                    if not os.path.isfile( des ) or override:
                        shutil.copy2( src, des )
                        message( "copy file: " + src, c = DEBUG  )
                    else:
                        message( "ignore file:" + src, c = DEBUG )
                        
    def is_enabled( self ):
        return len( self.window.folders() ) > 0