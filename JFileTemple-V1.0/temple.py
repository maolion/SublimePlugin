#< temple.py >
#encoding=utf8
#author=maolion( maolion.j@gmail.com )
#date=2012/10/22

import os
import sublime
from JFileTemple import CFG, altsep

def getTempleList():
    directory = CFG.get( "temple_dir" )
    items = os.listdir( directory )
    templist = []
    for item in items:
        path = altsep( os.path.join( directory, item ) )
        if os.path.isfile( path ):
            templist.append( path )
    templist.sort(key=lambda path: path.lower())
    return templist

def showTempleList( templist, callblack ):
    templist.sort(key=lambda path: os.path.basename( path.lower() ) )
    chooslist = []
    for item in templist:
        item = os.path.basename( item )
        info = os.path.splitext( item )
        chooslist.append( [
            "<temple>" + info[1],
            info[0]
        ] )
    sublime.active_window().show_quick_panel( chooslist, callblack )

def getTempleContent( temple ):
    content = ""
    with open( temple, "r" ) as fobj:
        content += fobj.read()
    return content