#< JNewFile.py >
#encoding=utf8
#author=maolion( maolion.j@gmail.com )
#date=2012/10/22

import os
import sublime, sublime_plugin

import JFileTemple
import temple
import Syntax


class JNewFile( sublime_plugin.WindowCommand ):
    __SyntaxInit = False
    def run( self, temp = None, dirs = None ):
        JFileTemple.moduleInit( __name__ )
        self.__view = self.window.new_file()
        if dirs and len(dirs) > 0:
            self.__view.settings().set( "default_dir", dirs[0] )

        message( LOC["CREATE_NEW_FILE"] )
        try:
            self.__tlist = temple.getTempleList()
            if not temp:
                temple.showTempleList( self.__tlist, self.__getTempleIndex )
            else:
                for item in self.__tlist:
                    if os.path.basename( item ) == temp:
                        self.__insertTempleContent( item )
                        break
        except Exception, e:
            sublime.error_message( LOC["CREATE_NEW_FILE_FAIL"] )
            message( "REALY_ERROR:" + str(e), c = DEBUG )

    def __getTempleIndex( self, index ):
        if index == -1: return None
        self.__insertTempleContent( self.__tlist[index] )

    def __insertTempleContent( self, temple_file ):
        message( "Choos: " + temple_file, c = DEBUG )
        message( LOC["WAIT_PLEASE"] )
        if JNewFile.__SyntaxInit == False:
            Syntax.init()
            JNewFile.__SyntaxInit = True

        message( LOC["GET_FILE_TEMPLE"] )            
        edit = self.__view.begin_edit()
        file_ext = os.path.splitext( temple_file )[1]
        self.__view.insert( edit, 0, temple.getTempleContent( temple_file ) )
        self.__view.set_name( "%s%s" % ( "Untitled", file_ext ) )
        syntax_path = Syntax.getSyntaxPath( file_ext )
        
        message( "Syntax Path: " + syntax_path, c = DEBUG )

        self.__view.set_syntax_file( syntax_path )
        self.__view.end_edit( edit )

        message( LOC["WRITE_FILE_TEMPLE_COMPLETE"] )