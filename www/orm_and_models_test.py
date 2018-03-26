
import www.orm
import asyncio
from www.models import User, Blog, Comment

#测试orm 查询 插入数据，针对test库user表

loop = asyncio.get_event_loop()
loop.run_until_complete(www.orm.create_pool(host='127.0.0.1', port=3306, user='root', password='xlh2018', db='awesome',loop=loop))
rs = loop.run_until_complete(www.orm.select('select * from users', None))
#rs = loop.run_until_complete(www.orm.execute('insert into `user` (id,name) values (4,"Ken")',None))
print('result: %s' % rs)
"""

#测试models
loop = asyncio.get_event_loop()
async def test():
    #创建连接池
    await www.orm.create_pool(loop=loop,user='root', password='xlh2018', db='awesome')

    #从models模块中创建User类实例，相当于对于user表操作，注意user表中必填的列属性
    u = User(id='123',name='Test', email='test@example.com', passwd='123456789', image='about:blank')

    #调用User类实例的save方法，保存数据入库
    await u.save()

#将协程丢入事件循环中
loop.run_until_complete(test())
"""

