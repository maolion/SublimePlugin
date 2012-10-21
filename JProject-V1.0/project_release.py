#< project_release.py >
#encoding=utf8
#author=maolion( maolion.j@gmail.com )
#date=2012-10-19

import os
import re
import json
import shutil
import time
import sublime, sublime_plugin
import project

from project import MESSAGE, DEBUG,XError

from StringTemple import *
from Queue import *

class project_release( sublime_plugin.WindowCommand ):
    """project_release 命令 实现了创建一个完整项目的发行版本"""
    FAIL_MESSAGE_FORMAT   = "%s\n  %s"
    COMMENT_RE_PATTERN    = re.compile( "(?:\s*//.*)|/\*[\S\s]*?\*/" )
    WRITESPACE_RE_PATTERN = re.compile( "^\s+$" )
    def run( self ):
        project.init( project_release.__module__ )

        self.__folders     = self.window.folders()
        self.__projectpath = self.__folders[0]
        self.__config      = None
        self.__files       = []
        self.__releasepath = ""
        self.__error       = ""

        MESSAGE( LOC["RELEASE_PROJECT"] )

        for func, msg, errmsg in [
            ( self.__getProjectConfigFile, ""                         , LOC["INVALID_PROJECT_CONFIG"] ),
            ( self.__releaseConfirm      , ""                         , "" ),
            ( self.__getProjectConfig    , LOC["GET_PROJECT_CONFIG"]  , LOC["GET_PROJECT_CONFIG_FAIL"] ),
            ( self.__checkProjectConfig  , LOC["CHECK_PROJECT_CONFIG"], LOC["INVALID_PROJECT_CONFIG"] ),
            ( self.__createReleaseDir    , LOC["CREATE_RELEASE_DIR"]  , LOC["CREATE_RELEASE_DIR_FAIL"] ),
            ( self.__copyFileToRelease   , LOC["COPY_FILE_TO_RELEASE"], LOC["COPY_FILE_TO_RELEASE_FAIL"] ),
            ( self.__replaceTag          , LOC["REPLACE_TAG"]         , LOC["REPLACE_TAG_FAIL"] ),
            ( self.__openReleaseDir      , ""                         , "")
        ]:
            MESSAGE( msg )
            try:
               if func(): break 
            except Exception, e:
                sublime.error_message(
                    project_release.FAIL_MESSAGE_FORMAT % (
                        LOC["RELEASE_PROJECT_FAIL"],
                        errmsg
                    )
                )
                if self.__releasepath:
                    shutil.rmtree( self.__releasepath, True )
                #DEBUG
                MESSAGE( "REAL-ERROR: " + str(e), c = DEBUG )

                return None

        MESSAGE( LOC["RELEASE_PROJECT_SUCCESS"] )        
    
    def __releaseConfirm( self ):
        if not DEBUG and not sublime.ok_cancel_dialog(
            "%s\n------------------\n%s" %(
                LOC["RELEASE_PROJECT"],
                LOC["RELEASE_BEFORE_TIP"]
            )
        ):
            self.window.open_file( self.__configfile )
            return True

    def __getProjectConfigFile( self ):
        configfile = None
        for directory in self.__folders:
            files = os.listdir( directory )
            for f in files:
                if os.path.splitext( f )[1].lower() == ".sublime-project":
                    configfile = os.path.join( directory, f )
                    break
            if configfile:
                break
        if configfile:
            self.__configfile = configfile
            
        else:
            raise XError( "Not found project config file" )

    def __getProjectConfig( self ):
        temp = ""
        with open( self.__configfile, "r" ) as fobj:
            temp += fobj.read()
        temp = re.sub( project_release.COMMENT_RE_PATTERN, "", temp  )
        self.__config = json.loads( temp )

    def __checkProjectConfig( self ):
        if not self.__config or not self.__config.has_key( "JProject" ):
            raise XError( "Invalid project config : " + self.__config )           

    def __createReleaseDir( self ):
        releasepath = os.path.join( 
            self.__projectpath, 
            "%s-V%s" % ( 
                self.__config["name"], 
                self.__config["release"]["variables"]["version"] 
            )
        )
        if os.path.isdir( releasepath ):
            if DEBUG:
                shutil.rmtree( releasepath, True )
            else:
                raise XError( "directory:<%s> already exists" % (releasepath) )
        
        os.makedirs( releasepath, 0777 )
        #DEBUG
        MESSAGE( "RELEASE_PATH: " + releasepath, c = DEBUG )

        self.__releasepath = releasepath

    def __copyFileToRelease( self ):
        releasepath           = self.__releasepath
        qdirs                 = Queue( 0, [] )
        ig_cfg                = self.__config["release"]["ignore"] 
        ig_file_re_patterns   = [ re.compile(pattern) for pattern in ig_cfg["file"] ]
        ig_folder_re_patterns = [ re.compile(pattern) for pattern in ig_cfg["folder"] ]
        
        #DEBUG
        MESSAGE(
            "   IG_FOLDER_P : %s\n"
            "   IG_FILE_P   : %s" % (
                ig_cfg["folder"],
                ig_cfg["file"]
            ), 
            c = DEBUG,
            prefix = ""
        )
        
        ignore = lambda s,p: bool( [
            r for r in p if re.search( r, s ) 
        ] )

        for folder in self.__folders:
            if len(self.__folders) == 1:
                root = folder
            else:
                root = os.path.dirname( folder )

            qdirs.put( folder )

            MESSAGE( ">> " + os.path.basename( folder ), prefix = "" )
            while True:
                if qdirs.empty(): break
                directory = qdirs.get()
                basedir = os.path.basename( directory )
                if ignore( basedir, ig_folder_re_patterns ): 
                    #DEBUG
                    MESSAGE( "   [-]" + basedir, c = DEBUG, prefix = "" )
                    continue
                
                new_directory = directory.replace( root, releasepath )
                if new_directory != releasepath:
                    os.makedirs( new_directory )
                
                #DEBUG
                MESSAGE( "   [+]" + basedir, c = DEBUG, prefix = "" )
                
                files = os.listdir( directory );
                for item in files:
                    if ignore( item, ig_file_re_patterns ): 
                        #DEBUG
                        MESSAGE( "      [-]" + item, c = DEBUG, prefix = "" )
                        continue

                    path = os.path.join( directory, item )
                    if os.path.isdir( path ):
                        qdirs.put( path )
                        continue
                    new_path = os.path.join( new_directory, item ) 
                    shutil.copyfile( path, new_path )
                    self.__files.append( new_path )
                    #DEBUG
                    MESSAGE( "      [+]" + item, c = DEBUG, prefix = "" )
        MESSAGE( "-------------------------------------------", c = DEBUG, prefix = "" )            

    def __replaceTag( self ):
        
        cfg          = self.__config["release"]
        ig_file_exts = cfg["ignore_file_exts"]
        data         = { "project_name" : self.__config["name"] }
        data.update( cfg["variables"] )
        tobj         = StringTemple( "", data )
        DATE_FORMAT  = LOC["DATE_FORMAT"]
        TIME_FOMAT   = "%H:%M:%S"
        DTIME_FORMAT = "%s %s" % ( DATE_FORMAT, TIME_FOMAT )
        replace_scope= CFG.get("replace_scope")

        #DEBUG
        MESSAGE(
            "   IG_FILE_EXTS : %s" % ( ig_file_exts ),
            c      = DEBUG,
            prefix = ""
        )

        for path in self.__files:
            ext = os.path.splitext( path )[1].lower()
            rpath = path.replace( os.path.dirname( self.__releasepath ), "" )
            if ext in ig_file_exts:
                MESSAGE( "   [IGNORE]" + rpath, c = DEBUG, prefix = "" )
                continue

            MESSAGE( "   [REPLACE]" + rpath, c = DEBUG, prefix = "" )
                
            localtime = time.localtime()
            tobj.expanData( {
                "FILE" : os.path.basename( path ),
                "PATH" : os.path.dirname( path ),
                "MDATE": time.strftime( DTIME_FORMAT, time.localtime( os.path.getctime( path ) ) ),
                "TIME" : time.strftime( TIME_FOMAT  , localtime ),
                "DATE" : time.strftime( DATE_FORMAT , localtime )
            } )

            temp    = ""
            with open( path, "r" )as fobj: temp += fobj.read()
            size    = len( temp )
            #temp    = temp.decode("utf8")
            content = ""
            for item in replace_scope:
                if ext not in item["file_ext"]: continue
                
                scopes  = []
                start   = 0
                pattern = re.compile( item["pattern"] )
                content = ""
                tobj.setTemple( "" )
                while start < size:
                    region = re.search( pattern, temp[start:] )
                    if region:
                        offset_start = start + region.start()
                        offset_end   = start + region.end()
                       # print offset_start, offset_end
                        part         = temp[ offset_start:offset_end ]
                        space        = temp[ start:offset_start ]
                        scopes.append( part )
                        if re.search( project_release.WRITESPACE_RE_PATTERN, space ):
                            tobj.expanTemple( space + part )
                        else:
                            content += tobj.parse() + temp[ start:offset_start ]
                            tobj.setTemple( part )
                            
                        start = offset_end
                    
                    else:
                        break
                content += tobj.parse() + temp[ start: ]
                #content = content.encode("utf8")
                #DEBUG
                if DEBUG:
                    MESSAGE( 
                        "            %s\n"
                        "            %s\n"
                        "            ---REPLACE SCOPE---\n"
                        "            %s\n" 
                        "            -------" % ( 
                            item["pattern"], 
                            ",".join( item["file_ext"] ),
                            "\n            ".join( [
                                re.sub( "\n", "\n            ", scope.decode("utf8") ) \
                                for scope in scopes
                            ] )
                        ),
                        c = DEBUG, 
                        prefix = "" 
                    )
            if content:
                try:
                    fobj = open( path, "w" ) 
                    fobj.write( content )
                except IOError:
                    raise IOError
                finally:
                    fobj.close() 
    
    def __openReleaseDir( self ):
        self.window.run_command(
            "open_dir", 
            {
                "dir" : self.__releasepath
            }
        );