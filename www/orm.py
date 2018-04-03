# !/usr/bin/env python
# -*- coding: UTF-8 –*-
'''
 -------------------------------
 @Author:    KEN
 @File:      orm.py.py
 @Date:      2018/3/22 17:15
 @Version:   1.0
 @Function:  异步mysql驱动，将常用的insert，delete，update，select操作封装成函数，方便调用
 @Useage:
 -------------------------------
 @Update log:

 -------------------------------
'''
import logging,asyncio
import aiomysql

__autoor__ = 'Ken'

# 记录sql命令
def log(sql, args=()):
    logging.info('SQL: %s' % sql)


# 创建连接池,__pool 默认编码为utf8 自动提交事务为True,不需要再commit提交事务
async def create_pool(loop, **kw):
    logging.info('Create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )

async def close_loop():
    logging.info('close database connection pool...')
    global __pool
    if __pool is not None:
        __pool.close()
        await __pool.wait_closed()
# =============================================
#
#                   SELECT
#
# =============================================
#
# sql语句占位符？，mysql占位符%s, 这里需要自动替换。
#
# 使用带参数SQL而不是自拼接SQL字符串以防SQL注入
#
# size定义了select获取指定量结果，不指定默认获取所有
#
# =============================================
async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        # 获取游标cursor，默认返回的是元祖tuple，这里可以指定元祖元祖为字典
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 调用cur 执行sql语句，execute接受2个参数，第一个为sql语句，第二个为占位符，此处该值可以避免使用字符串拼接处的sql注入
            await cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
    logging.info('rows returned: %s' % len(rs))
    return rs


# =============================================
#
#                   EXECUTE
#
# =============================================
#
# 封装了增删改的操作
#
# 在try commit时遇到错误就执行回滚
#
# =============================================
async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount  # 获取sql影响的行数
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected


# 创建用于几个占位符的字符串
# Usage: print(create_args_string(5))
# >>?, ?, ?, ?, ?
def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)


# =============================================
#
#            定义基类Field及其他列名的数据类型
#
# =============================================

class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s> % (self.__class__.__name__, self.column_type, self.name)'


class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)


class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


# =============================================
#
#                  元类
#
# =============================================
class ModelMeatclass(type):

    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        tableName = attrs.get('__table__', None) or name  # 获取表面，若没有则将类名称作为表名
        logging.info('found model: %s (table: %s)' % (name, tableName))
        mappings = dict()  # 保存列类型的对象
        fileds = []  # 记录列属性名
        primaryKey = None

        #这段代码是用来处理数据查找主键，检查主键是否和存在或冲突，将非主键的列属性值存入fileds，主键
        for k, v in attrs.items():
            if isinstance(v, Field):  # 是Field类型就保存进mappings 字典中
                logging.info('found mapping: %s ==> %s' % (k, v));
                mappings[k] = v
                if v.primary_key:  # 查找主键
                    if primaryKey:
                        raise StandardError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fileds.append(k)  # 将非主键列属性名存入列表中

        if not primaryKey:
            raise StandardError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)  # 删除attrs里属性，防止与实例属性冲突
        escaped_fields = list(map(lambda f: '`%s`' % f, fileds))    #将 fileds变成 `值`的形式便于sql识别处理
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey  # 主键属性名
        attrs['__fields__'] = fileds  # 其他列属性名
        # 以下为4中常用操作的sql语句模板，`%s` 反引号为了保证sql语句执行正确不与sql关键字冲突，传入的值自动进入格式化好的语句模板中
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into  `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fileds)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)


# =============================================
#
#                  元类
#
# =============================================
class Model(dict, metaclass=ModelMeatclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):     #拦截点运算符号（复习下多重继承-定制类）eg model.key --> model[key]
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)     #getartt返回属性值，eg a = ClassA() getattr(a, 'key') 返回ClassA实例a属性key的值

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default  # 判断对象是否调用
                logging.info('useing default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    '''
    classmethod
    修饰函数不需要实例化，不需要self参数，但第一个参数需要式表示自身的cls参数，可以用来调用类的属性，类的方法，实例化对象
    eg:
    class A(object):
        bar = 1
        ...
        @classmethod
        def func1(cls):
            print('func2:',cls.bar)
            
    A.func1()
    >>> func2: 1
    '''

    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        ' find objects by where clause.'
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit',None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit,int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit,tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        'find number by select and where'
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls, pk):
        'find object by primary key'
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)

    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)