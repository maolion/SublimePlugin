#encoding=utf8
#< StringTemple.py >
#author=maolion( maolion.j@gmail.com )
#date=2012/10/18
"""StringTemple 模块包含一个可以完成简单字符串模板替换工作的类
    StringTemple 类
"""
import re

class StringTemple():
    """该类定义了处理简单字符串模板的接口
目前它只能准确的完成将字符串里的替换标签(格式是：${替换标签名},${替换标签名}[索引]
${替换标签名}.子替换标签名 )替换成与绑定数据相对应的值。

构造器：
StringTemple( temple, data, default = None )
    @param {String} temple 字符串模板
    @param {dict}   data 与模块绑定的字典
    @param {dict}   [default] 默认字典  
    """

    __VARIABLE_RE_PATTERN = re.compile(\
        r"\${([A-Z_a-z][A-Z_a-z0-9]*)}(?:(?:\[(\d+)\])|(?:\.([A-Z_a-z][A-Z_a-z0-9]*)))?"\
    )

    def __init__( self, temple, data, default = None ):
        self.__temples  = [ str( temple ) ]
        self.__data     = type( data ) == dict and data or {}

        self.__default  = type( default ) == dict and default or {}
        self.__cache    = ""
        self.__append   = False
        #public
        self.undefined  = ""

    def parse( self, data = None ):
        """解析模板，并返回解析结果
parse( data = None )
    @param {dict/String} 立即设定的字典和模板
    @return {String}
"""
        if type(data)   == dict:
            self.setData( data )
        elif type(data) == str:
            self.setTemple( data )
        temple = ""    
        if not self.__cache :    
            temple = "".join( self.__temples )
        elif self.__append:
            temple = self.__temples[-1]
        if len(temple):
            self.__append = False        
            data = self.__default
            data.update( self.__data )

            self.__cache += self.replaceVariable( temple, data )
        return self.__cache
        
    def replaceVariable( self, temple, data ):
        """
搜索模板里的替换标签，然后逐个替换它们,并返回替换结果
replaceVariable( temple, data )
    @param  {String} temple 字符串模板
    @param  {dict} data 字典
    @return {String}
"""
        if len( temple ) == 0: return ""

        if not data: return ""

        while True:
            matchs = re.findall( StringTemple.__VARIABLE_RE_PATTERN, temple )
            if not matchs or len(matchs) == 0: break
            #temple = temple.decode("utf8")
            temp   = ""
            size   = len(temple)
            start  = 0
            for item in matchs:
                key     = item[0]
                pattern = "\${%s}" % ( key )
                obj     = data.has_key( key ) and data[key] or self.undefined
                key     = ""

                if len(item[1]):
                    key = item[1]
                    pattern += "\[%s\]" % ( key )
                elif len(item[2]):
                    key = item[2] 
                    pattern += "\." + item[2] 
                if obj != self.undefined:
                    if type( obj ) == dict and obj.has_key( key ):
                        obj = obj[key]
                    elif type( obj ) == list and len(item[1]) and len(obj) > int(key):
                        obj = obj[int(key)]
                    elif len(key):
                        obj = self.undefined
                if obj != self.undefined and type( obj ) == dict:
                    obj = obj.has_key( key ) and obj[key] or self.undefined
                
                part   = temple[ start : size ]
                region = re.search( pattern, part )
                if region:
                    offset_start = region.start() + start
                    offset_end   = region.end() + start
                    temp        += temple[ start : offset_start ]
                    part         = temple[ offset_start : offset_end ]
                    temp        += re.sub( pattern, str(obj), part, 1 )
                    start        = offset_end
                    
            if start < size:
                temp += temple[ start: ]
            temple = temp
    
        return temple


    def setDefaultData( self, data ):
        """修改默认字典
setDefaultData( data )
    @param {dict} data
"""
        if type(data) == dict:
            self.clearCache()
            self.__default = data

    def setData( self, data ):
        """修改字典
setData( data )
    @param {dict} data
"""
        self.clearCache()
        if type(data) == dict:
            self.__data = data
        else:
            self.__data = {}

    def expanData( self, data ):
        """扩大字典
expanData( data )
    @param {dict} data
"""
        if type( data ) == dict:
            for key in data.keys():
                if self.__data.has_key( key ) or self.__default.has_key( key ):
                    self.clearCache()
                    break
            self.__data.update( data )


    def expanTemple( self, temple ):
        """扩大字符串模板
expanData( temple )
    @param {Sring} temple
"""
        self.__append  = True
        self.__temples.append( temple )     
                
    def setTemple( self, temple ):
        """修改字符串模板
expanData( temple )
    @param {String} temple
"""
        self.clearCache()
        self.__temples = [ str( temple ) ]
    
    def clearCache( self ):
        """清除已经保存下的临时缓存数据"""
        self.__append = False
        self.__cache = ""

if __name__ == "__main__":
    print "\n\n\n------------------------------------------------------------------\n\n\n"
    tmp = StringTemple( 
        "\
        Hello,${name}\n\
        FullName:${Info}.name # age:\n\
        email:${Email}\n\
        QQ:${QQ}[0]\n\
           ${QQ}[1]\n\
           ${QQ}[2]\n\
        URL:${URL}\n",
        {
            "name" : "${Jiang}",
            "Jiang": "Joye",
            "Email": "maolion.j@gmail.com",
            "Info" : {
                "name" : "YiWei.Jiang",
                "age" : 19
            },
            "QQ" : [ "540730881", 540730882 ],
            "URL": "404(Not Found)"
        }
    )
    print tmp.parse() #new
    print tmp.parse() #cache
    tmp.expanTemple("\n------------------------------------------------------------------")
    print tmp.parse() #append
    tmp.expanData( { "date" : "2012/10/18" } )
    tmp.expanTemple("\n\t\t\t\t\t\t\t\t\t\t\t\t${date}")
    print tmp.parse() #append
    print tmp.parse() #cache
    print tmp.parse( "${name}: Tested!" ) #new
      
    
