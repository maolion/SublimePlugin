#< JProjectCreate.py >
#encoding=utf8
#author=(  )
#date=2012/10/21

import os
import sublime, sublime_plugin
import JProject
from JProject import message, altsep, XError
from Queue import *
from StringTemple import *

#不靠谱
SUBLIME_APP_PATH = os.path.join(
    os.path.dirname( os.path.dirname( os.__file__ ) ),
    "sublime_text.exe"
)


class JProjectCreateCommand( sublime_plugin.WindowCommand ):
    """JProjectCreateCommand 命令 实现了项目的创建和自动打开创建的项目"""

    def run( self ):
        #将LOC GFG DLOC等这些变量定义到当前模块 
        JProject.moduleInit( __name__ )

        self.__dict         = {
            "project_name"      : "",
            "project_directory" : ""
        }

        self.__project_name = ""
        self.__projectconfig= os.path.join( PPATH, "project.config" )
        default_directory   = os.path.expanduser( "~\\My Documents\\" )
        self.__input        = None
        self.__terr         = StringTemple( "", {} )

        #请求输入队列
        self.__iqueue       = Queue( 0, [
            #( <property>, <status message>, <caption>, <init input>, [<callback>] )

            #input project name
            (
                "project_name",                                             
                LOC["CREATE_PROJECT"] + ">" +  LOC[ "INPUT_PROJECT_NAME" ], 
                LOC["INPUT_PROJECT_NAME"],                                  
                "",                                                         
                None                                                        
            ),
            #input project directory
            (
                "project_directory",                                       
                LOC["CREATE_PROJECT"] + ">" +  LOC[ "INPUT_PROJECT_DIR" ], 
                LOC["INPUT_PROJECT_DIR"],                                  
                ( lambda : os.path.join( 
                    len( CFG.get( "work_space") ) and CFG.get("work_space") or default_directory,
                    self["project_name"] 
                ).replace("\\","/") ),                                                     
                [ self.__createProjectDestory, self.__createProjectConfig, self.__openProject ]                             
            )
        ] )
        
        self.__showInputPanel()


    def __showInputPanel( self, new = True ):
        if new:
            if self.__iqueue.empty():return None
            self.__input = self.__iqueue.get()
        elif self.__input == None:
            return None

        message( self.__input[1] )
        
        initinput = self.__input[3]
        if initinput and type(initinput) != str:
            initinput = initinput()
        
        self.window.show_input_panel( 
            self.__input[2],
            initinput, 
            self.__onInputDone, 
            None, 
            None 
        )


    def __onInputDone( self, instr ):
        message( LOC["WAIT_PLEASE"] )
        while True:
            if len(instr) == 0:
                self.__showInputPanel(False)
                return
            break
        self[self.__input[0]] = instr
        callbacks = self.__input[4]

        try:
            if callbacks:
                    for callback in callbacks:
                        callback()
            self.__showInputPanel()
        except Exception, e:
            sublime.error_message( self.__terr.parse() )
            self.__terr.setTemple("")
            message( "REAL-ERROR: " + str(e), c = DEBUG )
            return None
            
    def __createProjectDestory( self ):
        message( LOC["WAIT_PLEASE"] )
        name      = self["project_name"]
        directory = self["project_directory"] = self["project_directory"].replace( "\\", "/" )
        self.__terr.expanData({
            "title"       : LOC["CREATE_PROJECT_FAIL"],
            "error"       : LOC["CREATE_PROJECT_DIR_FAIL"],
            "description" : LOC["DIRECTORY_EXIST"],
            "file"        : directory
        })
        self.__terr.setTemple( 
            "${title}\n"
            "${error}\n"
            "${description}\n"
            "${file}" 
        )
        if os.path.isdir( directory ):
            raise XError( "file:<%s> already exists" % (directory) )
        os.makedirs( directory, 0777 )
        CFG.set( "work_space", os.path.dirname( directory ) )
        sublime.save_settings("JProject.sublime-settings")
        message( LOC["CREATE_PROJECT_DIR_SUCCESS"] )

    def __createProjectConfig( self ):
        message( LOC["CONFIGING_PROJECT"] )
        name     = self["project_name"] + ".sublime-project"
        filename = os.path.join( self["project_directory"], name ).replace( "\\", "/" )
        self.__terr.expanData({
            "title" : LOC["CREATE_PROJECT_FAIL"],
            "error" : LOC["CONFIG_PROJECT_FAIL"],
            "file"  : filename
        })
        self.__terr.setTemple( 
            "${title}\n"
            "${error}\n"
            "${file}"
        )
        d = {
            "project_name" : self["project_name"]
        }
        temp = StringTemple( "", self.__dict )
        content = ""
        with open( self.__projectconfig, "r" ) as fobj:
            content += fobj.read()
        try:
            fobj = open( filename, "w" )
            fobj.write( temp.parse( content ) )
        except Exception, e:
            raise e
        finally:
            fobj.close()

        self["project_config_file"] = filename
        message( LOC["CONFIG_PROJECT_SUCCESS"] )    
    
    def __openProject(self):
        message( LOC["OPENNING_PROJECT"] )
        os.spawnv(
            os.P_NOWAIT,
            SUBLIME_APP_PATH,
            [ '\k', '"%s"' % ( self["project_config_file"] ) ]
        )
        message( LOC["CREATE_PROJECT_SUCCESS"] )

    def __getitem__( self, key ): return self.__dict[key]
    def __setitem__( self, key, value ): self.__dict[key] = value

