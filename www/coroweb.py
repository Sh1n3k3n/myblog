#!/usr/bin/env python
# -*- coding: UTF-8 –*-
''' 
 -------------------------------
 @Author:    KEN
 @File:      coroweb.py
 @Date:      2018/3/26 15:59
 @Version:   1.0
 @Function:

    coroweb模块实现了对请求处理的框架，将站点，请求，请求方法做了标准化处理实现了aiohttp的基本功能


 @Useage:    
 -------------------------------
 @Update log:
 
 -------------------------------
'''

import asyncio, os, inspect, logging, functools

from urllib import parse

from aiohttp import web

from www.apis import APIError


# =============================================
#
#            定义get post装饰器
#
# =============================================
#  装饰后增加了method route属性便于后续识别请求类型
#  以及对于path的进行路由处理
# =============================================
def get(path):
    '''
    Define decorator @get('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator

def post(path):
    '''
    Define decorator @post('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator


# =============================================
#
#            定义参数获取的方法
#
# =============================================
#   主要使用了inspect模块的signature获取方法的标签及参数
#   通过一系列的parameters参数的kind类型匹配返回结果
# =============================================


def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)

def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)

def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':       #找到request请求，并判断request值类型是否符合标准
            found = True
            continue
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
    return found

# =============================================
#
#            定义请求处理器
#
# =============================================
# 初始化处理器，保存请求的站点，方法
# 对请求的方法进行分析将分析结果存入私有属性中
# 根据实际的请求类型content_type进行进行处理，并保存参数
# 过滤参数并检查，再将其传入指定的方法进行处理#
# =============================================

class RequestHandler(object):

    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        #定义私有属性，并调用之前定义好的函数参数处理方法赋值
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):  #定义类调用方法
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:   #若从函数处理方法中获取到参数
            if request.method == 'POST':        #这里的request是通过 最初的get post装饰器处理过的 自带__method__ 值，以此判断request的操作类型
                if not request.content_type:    #检查request 是否含有content_type类型标识，没有报错
                    return web.HTTPBadRequest('Missing Content-Type.')
                ct = request.content_type.lower()   #ct变量赋于content_type值，并变成小写 便于后续处理
                #下面是针对不同content_type类型进行处理
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':
                qs = request.query_string   #获取的是url? 后面的所有值
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        # parse.parse_qs 作用是解析字符串参数，返回字典
                        # eg: test=a&test2=b&test=c
                        # >>> {'test':'a','test2':'b','test3':'c'}
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args:
                # remove all unamed kw:
                # copy为空字典，如果kw有值和named_kw_args中的值进行匹配，将值存入copy中，最后将所有匹配上的值 重新赋予kw 意将kw去除unamed的值
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        # check required kw:
        if self._required_kw_args:
            for name in self._required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest('Missing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)

#注册静态文件
def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')  #获取站点路径并拼接上 static目录
    app.router.add_static('/static/', path) #定义'/static/'路由
    logging.info('add static %s => %s' % ('/static/', path))


#每次只能注册一个url处理函数
def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))

#批量注册url处理函数，只需提供模块路径，自动导入其中的函数进行注册
def add_routes(app, module_name):
    n = module_name.rfind('.')  #查找'.'在字符串中的位置
    if n == (-1):
        mod = __import__(module_name, globals(), locals())      #动态加载模块 等价于import module_name，常用于加载某个文件夹下的经常变换名称的模块，列入插件，扩展
    else:
        name = module_name[n+1:]    #将.后面的字符串赋值给name
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)   #from ’.‘前面的字符串为模块名模块名 import '.'后面名称为name值的模块
    for attr in dir(mod):   #读出mod中所有的类，实例及函数对象
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):        #只对可调用的函数进行注册
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                add_route(app, fn)  #注册所有的url处理方法（方法含method和route）