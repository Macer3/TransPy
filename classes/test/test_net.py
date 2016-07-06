# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
from transpy.readwrite.rw_txt import *
import transpy as tp
import os
from transpy.classes.convert import get_net_data
import nose.tools as nt
import numpy as np

# 得到当前脚本的绝对路径
path = os.path.split(os.path.realpath(__file__))[0]
data = load_txt_table('./transpy/test/data/street.asc',
                      names=['ID', 'Length', 'Dir', 'capacity', 'AB_flow',
                             'BA_flow', 'AB_speed', 'BA_speed', 'AB_times',
                             'BA_times', 'AB_v/c', 'BA_v/c'])
point_data = load_point_geo_txt('./transpy/test/data/node.geo',
                                ptype='long_lat')
line_data = load_line_geo_txt('./transpy/test/data/street.geo',
                              ptype='long_lat')

street_data = tp.geo.build_point_line_connection(point_data,
                                                 line_data, ptype='long_lat')

street_data = tp.merge_two_table(street_data, data)
# noinspection PyTupleAssignmentBalance
data, idx, r_idx, trace = get_net_data(street_data,
                                       fields=['ID', 'Length', 'Dir',
                                               'capacity',
                                               'AB_flow', 'BA_flow', 'AB_speed',
                                               'BA_speed', 'AB_times',
                                               'BA_times', 'AB_v/c', 'BA_v/c'])
