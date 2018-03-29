#!/usr/bin/env python
# -*- coding: UTF-8 –*-
''' 
 -------------------------------
 @Author:    KEN
 @File:      config_default.py
 @Date:      2018/3/29 10:59
 @Version:   1.0
 @Function:  开发环境配置
 @Useage:    
 -------------------------------
 @Update log:
 
 -------------------------------
'''

configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'xlh2018',
        'db': 'awesome'
    },
    'session': {
        'secret': 'Awesome'
    }
}