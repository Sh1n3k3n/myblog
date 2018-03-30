#!/usr/bin/env python
# -*- coding: UTF-8 –*-
''' 
 -------------------------------
 @Author:    KEN
 @File:      handlers.py
 @Date:      2018/3/26 18:24
 @Version:   1.0
 @Function:  
 @Useage:    
 -------------------------------
 @Update log:
 
 -------------------------------
'''
__author__ = 'Michael Liao'

' url handlers '

from www.coroweb import get, post

import asyncio, re, time, json, logging, hashlib, base64

from www.models import User, Comment, Blog, next_id

'''
'example'
@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }
'''

# =============================================
#
#            重新定义了index的内容
#
# =============================================
#  summary及blogs会被blogs.html 通过jinja2模块抽取出来填充至html展示
#  app的datetime_filter 就是为了处理这里的时间让jinja2加载的过滤器
# =============================================
@get('/')
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }

