#< Queue.py >
#encoding=utf8
#author=maolion( maolion.j@gmail.com )
#date=2012/10/18
"""Queue 模块提供了实现队列数据结构的接口
    Queue 类
    -----------------
    下列为 使用 Queue类时 可能抛出的异常
    QueueRangeException
    QueueFullException
    QueueEmptyException
"""
from types import ListType, TupleType

class Queue():
	"""Queue 实现队列的类
构造器:
Queue( maxsize = 0, queue = None )
	@param {Integer} [maxsize] 队列最大元素数量
	@param {list}    [queue] 队列初始元素集合
	"""
	ListType = (
		ListType,
		TupleType  
	)
	def __init__( self,maxsize = 0, queue = None ):
		self.__list = []
		self.__maxsize = long(maxsize)
		if( queue and type(queue) in Queue.ListType ):
			if( maxsize and len(queue) > maxsize ):
				raise QueueRangeException
			else:
				self.__list.extend( queue )

	def get( self ):
		"""弹出队列第一个元素，并返回该元素\nget()"""
		if( self.__list ):
			item = self.__list[0]
			del self.__list[0]
			if( self.__list ): self._list = self.__list[ 1: ]
			return item	
		else:
			raise QueueEmptyException, "this queue is empty"

	def put( self, item ):
		"""添加一个元素到队列尾部\n
put(item)
	@param {*} item  新元素
""" 
		if( not self.full() ):
			self.__list.append( item )
		else:
			raise QueueFullException, "this queue Fulled"
	def size(self):
		"""返回队列的大小（包含元素数量）
size()
	@return {Integer}
""" 
		return len( self.__list )
	def empty(self):
		"""检查队列是否为空队列
empty()
	@return {Boolean}
"""
		return bool( self.__list ) == False
	def full(self):
		"""检查队列是否已满
full()
	@return {Boolean}
""" 
		return bool(self.__maxsize) and self.__maxsize <= len( self.__list ) or False
	def __len__(self):return self.size()
	def __repr__(self): return repr( self.__list )
	def __iter__(self):
		for d  in self.__list:
			yield d

class QueueRangeException(Exception):pass
class QueueFullException(Exception):pass
class QueueEmptyException(Exception):pass
