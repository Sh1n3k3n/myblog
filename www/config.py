#!/usr/bin/env python
# -*- coding: UTF-8 –*-
''' 
 -------------------------------
 @Author:    KEN
 @File:      config.py
 @Date:      2018/3/29 10:58
 @Version:   1.0
 @Function:  配置文件加载器
 @Useage:    
 -------------------------------
 @Update log:
 
 -------------------------------
'''

import www.config_default


# =============================================
#
#           派生Dict类，实现dcit.key取值
#
# =============================================
class Dict(dict):

    def __init__(self ,names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            '''
            zip函数 将可迭代的对象对应位置的元素组成元祖并返回由该元祖组成的列表，由最短的迭代对象长度决定元祖个数
            eg： a=[1,2,3] b=[4,5,6,7]  zipped = zip(a,b) --> [(1,2),(3,4),(5,6)]  解压缩返回一个二维矩阵 zip(*zipped) --> [(1,2,3),(4,5,6)]
            '''
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

def merge(defaults, override):
    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r

def toDict(d):
    D = Dict()
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D

configs = www.config_default.configs


try:
    import www.config_override
    configs = merge(configs, www.config_override.configs)

except ImportError:
    pass

configs = toDict(configs)

#test

print(configs.db)