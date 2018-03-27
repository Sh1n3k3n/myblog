#!/usr/bin/env python
# -*- coding: UTF-8 –*-
''' 
 -------------------------------
 @Author:    KEN
 @File:      apis.py
 @Date:      2018/3/26 15:50
 @Version:   1.0
 @Function:  Json api definition.
 @Useage:    
 -------------------------------
 @Update log:
 
 -------------------------------
'''

import json, logging, inspect, functools

# =============================================
#
#            定义API接口错误类
#
# =============================================

class APIError(Exception):

    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message

class APIValueError(APIError):

    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid' ,field, message)

class APIResourceNotFoundError(APIError):

    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:not found', field, message)

class APIPermissionError(APIError):

    def __init__(self, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', message)