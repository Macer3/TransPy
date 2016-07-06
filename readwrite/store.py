# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np
import os
import re


#############################################################
# 读取txt格式的表格文件函数版本1, 不能解决缺失值问题, 所以废弃了
#############################################################

def split_data(data, have_splited, sep=None, count_pos=None):
    """
    主要是配合
    将data中的每一个字符串都用sep划分，划分后的每一个字符串都为一个元组

    同时对于需要确定字符串的最大长度的，给定相应的count_pos
    Parameters
    ----------
    data :
    have_splited :
    sep :
    count_pos :

    Returns
    -------

    """
    if count_pos is not None:
        max_len = [0 for mem in count_pos]

    for i in range(len(data)):
        data[i] = tuple(data[i].strip().split(sep))
        if count_pos is not None:
            for j, num in enumerate(count_pos):
                new_len = len(data[i][num])
                if new_len > max_len[j]:
                    max_len[j] = new_len

    have_splited[0] = 1
    if count_pos is not None:
        return max_len


def auto_format(data, have_splited, sep=None):
    """用来1自动确定txt/csv格式文件中每列的格式,整形的定为int32, 小数定为float64
    字符串型的取最大的长度
    """
    formats = []
    unicode_pos = []
    sample = data[0].strip().split(sep)

    for mem in sample:
        assert isinstance(mem, str)
        try:
            int(mem)
            formats.append('i4')
        except ValueError:
            try:
                float(mem)
                formats.append('f8')
            except ValueError:
                unicode_pos.append(len(formats))
                formats.append('U')

    if len(unicode_pos) > 0:
        unicode_len = split_data(data, have_splited, sep, unicode_pos)
        for _pos, _len in zip(unicode_pos, unicode_len):
            formats[_pos] = 'U' + str(_len)

    return formats


# todo 对于多个分隔符，分隔符里面有空格的情况，还有字符串带引号，
# 将来要用正则表达式来完善
# 这里先假设如果是字符串的话会有""符号
# todo 对于有format文件的情况还没处理
def load_txt_table(file, sep=',', skip_header=0, skip_footer=0,
                   encoding=D_ENCODE, names=0, formats=0):
    """从txt/csv文件读取表格数据

    Parameters
    ----------
    formats : 0/list
        file每列对应的数据格式, 为0时先寻找是否存在与file配对的格式(*.format)文件,
        若存在则从格式文件中读取格式, 若不存在则根据auto_format()函数自动确定格式.
        为list时, list中的每个元素依次对应file每列的格式.
    names : 0/1/list
        为0与list时的效果同formats. 为1时则从file文件的第一个有效行读取域的名称
    file : path
        要读取的文件路径

    sep : string
        分隔符

    skip_header : integer
        开头几行不要

    skip_footer : integer
        结尾几行不要

    encoding : 编码方式
        默认为utf-8,中文系统常用到gbk


    Return
    ------
    A dictionary keyed by line's ID, stores scoordinates or long_lat
    in numpy structured array
    """
    with open(file, 'r', encoding=encoding) as f:
        file = f.readlines()

    have_splited = [0]
    sample = file[skip_header].strip().split(sep)
    if names == 1:
        names = sample
        skip_header += 1
    elif names == 0:
        names = ['f' + str(i) for i in range(len(sample))]

    num = len(file)
    file = file[skip_header: (num - skip_footer)]
    if formats == 0:
        formats = auto_format(file, have_splited, sep)

    if have_splited[0] == 0:
        split_data(file, have_splited, sep)

    data = np.array(file, dtype={'names': names, 'formats': formats})
    return data
