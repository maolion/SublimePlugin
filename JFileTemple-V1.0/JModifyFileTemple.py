#< JModifyFileTemple.py >
#encoding=utf8
#author=maolion( maolion.j@gmail.com )
#date=2012/10/22

import os
import sublime, sublime_plugin

import JFileTemple
import temple



class JModifyFileTempleCommand( sublime_plugin.WindowCommand ):
    __SyntaxInit = False
    def run( self ):
        JFileTemple.moduleInit( __name__ )
        try:
            self.__tlist = temple.getTempleList()
        except Exception, e:
            sublime.error_message( LOC["GET_TEMPLE_LIST_FAIL"] )
            message( "REALY_ERROR:" + str(e), c = DEBUG )

        temple.showTempleList( self.__tlist, self.__openTempleFile )    
            
    def __openTempleFile( self, index ):
        if index == -1: return None
        self.window.open_file( self.__tlist[index] )

class JAddFileTempleCommand( sublime_plugin.WindowCommand ):

    def run( self ):
        newview = self.window.new_file()
        newview.settings().set('default_dir',  CFG.get("temple_dir") )

class JOpenTempleDirectoryCommand( sublime_plugin.WindowCommand ):

    def run( self ):
        self.window.run_command( "open_dir", {
            "dir" : CFG.get("temple_dir")
        } )