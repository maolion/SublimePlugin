#< Syntax.py >
#encoding=utf8
#author=maolion( maolion.j@gmail.com )
#date=2012/10/22

import os
import re
import sublime

__Syntax = {}
PPATH = sublime.packages_path()
FILETYPE_RE_PATTERN = re.compile( "<key>fileTypes</key>[\\s\\S]*?(?:</array>|<array/>)" )
FILEEXT_RE_PATTERN = re.compile( "<string>([^<]*)</string>" )

def init():
    __analyzeSyntaxConfigFiles(
        __getSyntaxConfigFiles(
            __getPluginsDirectory()
        )
    )

def __getPluginsDirectory():
    items = os.listdir( PPATH )
    plugins_directory = []
    for item in items:
        path = os.path.join( PPATH, item )
        if os.path.isdir( path ):
            plugins_directory.append( path )
    return plugins_directory   

def __getSyntaxConfigFiles( directorys ):
    syntax_config_files = []
    for directory in directorys:
        items = os.listdir( directory )
        for item in items:
            path = os.path.join( directory, item )
            if os.path.isfile( path ) and item[-11:] == ".tmLanguage":
                syntax_config_files.append( path )
    return syntax_config_files

def __analyzeSyntaxConfigFiles( files ):
    for filepath in files:
        
        content = __readFileContent( filepath )
        region = re.search( FILETYPE_RE_PATTERN, content )
        if region:
            content = content[ region.start() : region.end() ]
            fileexits = [ "." + ext.lower() for ext in  re.findall( FILEEXT_RE_PATTERN, content ) ]
            __Syntax[filepath] = fileexits
    return __Syntax

def __readFileContent( path, mode = "r" ):
    content = ""
    with open( path, mode ) as fobj:
        content += fobj.read()
    return content

def getSyntaxPath( fileext ):
    fileext = fileext.lower()
    syntax_path = ""
    for path in __Syntax.keys():
        if fileext in __Syntax[path]:
            syntax_path = path
            break
    if not syntax_path:
        language = fileext[1:]
        path = os.path.join( PPATH, language )
        syntax_path = os.path.join( path, language + ".tmLanguage" )

    return syntax_path

   
