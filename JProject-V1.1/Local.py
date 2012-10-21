#< Local.py >
#encoding=utf8
#author=maolion( maolion.j@gmail.com )
#date=2012/10/18
"""
Local 模块提供了一些对本地化配置操作的接口
    Local 类
    -----------------
    下列为 使用 Local类时 可能抛出的异常
    LocalError
    LoadLocalConfigError
"""
import os
import json

class Local():
    """一个处理本地化配置的简单类
构造器：
Local( localfile, default )
    @param {String} localfile 本地化配置文件所在地址
    @param {dict}   [default] 默认配置
    """    
    __cache    = {}
    __lasttiem = {}
    def __init__( self, localfile, default = None ):
        self.__config  = None
        temp           = ""
        self.__default = type(default) == dict and default or {}
        if Local.__cache.has_key(localfile) and Local.__lasttiem[localfile] == os.path.getmtime( localfile ):
            self.__config = Local.__cache[localfile]
        else:
            try:
                with open( localfile, "r" ) as f:
                    temp      = f.read()
                self.__config = json.loads( temp )
                temp          = None

            except Exception:
                raise LoadLocalConfigError( localfile )

            Local.__lasttiem[localfile]    = os.path.getmtime( localfile )
            Local.__cache[localfile]       = self.__config

        #if default and type( default ) == dict:
        #    for key in default.keys():
        #        if not self.__config.has_key( key ) or self.__config[key] == None:
        #            self.__config[key] = default[key]    
    
    def get( self, key ):
        """"""
        if self.__config.has_key( key ):
            return self.__config[key]
        elif self.__default.has_key( key ):
            return self.__default[key]
        return ""

    def copy( self ): 
        return self.__config.copy()

    def __getitem__( self, key ): return self.get( key )



class LocalError( Exception ):
    def __init__( self, message = "" ):
        self.__message = str( message )

    def __str__( self ):
        return "%s: %s" % ( str( self.__class__ )[8:-2], self.__message )

class LoadLocalConfigError( LocalError ):pass


