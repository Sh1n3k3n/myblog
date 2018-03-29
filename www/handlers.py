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


'example'
@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }

@get('/hello')
async def hello(request):
    return '<h1>Hello World!</h1>'

