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

from www.coroweb import get

import asyncio

'example'
@get('/')
async def index(request):
    return '<h1>Awesome</h1>'

@get('/hello')
async def hello(request):
    return '<h1>Hello World!</h1>'

