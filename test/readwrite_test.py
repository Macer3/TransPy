# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
from transpy.readwrite.rw_txt import *
import transpy as tp
import os

# 得到当前脚本的绝对路径
path = os.path.split(os.path.realpath(__file__))[0]

# a = load_txt_table(DIR+'/data/street.asc')

street_file = 'D:\\Documents\\Python Scripts\\Achieve~！#\\test\
\\数据结构\\transcad\\street\\street.BIN'
point_file = 'D:\\Documents\\Python Scripts\\Achieve~！#\\test\
\\数据结构\\transcad\\geo\\node.geo'
line_file = 'D:\\Documents\\Python Scripts\\Achieve~！#\\test\\数据结构\
\\transcad\\geo\\street.geo'
# point_data = load_point_geo_txt(point_file, ptype='long_lat')
# line_data = load_line_geo_txt(line_file, ptype='long_lat')
# street_table = load_bin(street_file)
# arc_list = build_point_line_connection(point_data, line_data,
#                                        ptype='long_lat')
# street_table = pack_data(street_table)
# street_table2 = merge_two_table(arc_list, street_table)


## 测试引号替换
# DIR = "D:\Documents\PythonS\\transpy\\test\\transpy\\test\data\Weihai\\"
# line_table = load_txt_table(DIR + 'street.txt',
#                             names=['ID', 'LENGTH', 'DIR', 'Layer', 'Handle',
#                                    'time',
#                                    'speed', 'capacity', 'AB_flow',
#                                    'BA_flow', 'names'], encoding='gbk')