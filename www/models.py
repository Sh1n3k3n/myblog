#!/usr/bin/env python
# -*- coding: UTF-8 –*-
''' 
 -------------------------------
 @Author:    KEN
 @File:      model.py
 @Date:      2018/3/23 16:30
 @Version:   1.0
 @Function:  
 @Useage:    
 -------------------------------
 @Update log:
 
 -------------------------------
'''

import time, uuid

from orm import Model, StringField, BooleanField, FloatField, IntegerField, TextField

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

#=============================================================================
#
# default 参数可以让ORM自己填入缺省值
#
# 时间用flot类型而不是datetime为了数据库不做时区转换问题，后续做一个float to str的转换即可
#
#==============================================================================


class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)

class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)