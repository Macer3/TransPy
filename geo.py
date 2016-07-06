# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np


def build_point_line_connection(point_data, line_data, ptype='LONG_LAT'):
    """将独立的点与线地理数据之间建立拓扑联系.

    parameter
    ---------
    point_data : structured array
        点地理文件.

    line_data : dict
        线地理文件.

    ptype : {'LONG_LAT', 'XY'}, optional
        指明地理文件中是经纬度还是坐标作为匹配的标准. Default : 'LONG_LAT'

    Return
    ------
    arc_list : structured array
        An structured array with fields ``['ID', 'START_NODE', 'END_NODE']``,
        缺失的地方补为0.
    """
    if ptype == 'XY':
        x_pos = 'X'
        y_pos = 'Y'
    elif ptype == 'LONG_LAT':
        x_pos = 'LONG'
        y_pos = 'LAT'
    else:
        raise ValueError("Wrong position-type, use 'XY' or 'LONG_LAT'.")
    dtype = np.dtype({'names': ['ID', 'START_NODE', 'END_NODE'],
                      'formats': [np.uint16, np.uint16, np.uint16]})
    arc_list = np.zeros((len(line_data),), dtype=dtype)
    i = 0
    for ID, pos in line_data.items():
        start_x = pos[0][x_pos]
        start_y = pos[0][y_pos]
        end_x = pos[-1][x_pos]
        end_y = pos[-1][y_pos]
        try:
            arc_list[i]['ID'] = ID
            arc_list[i]['START_NODE'] = point_data['ID'][
                (point_data[x_pos] == start_x) & (point_data[y_pos] == start_y)]
            arc_list[i]['END_NODE'] = point_data['ID'][
                (point_data[x_pos] == end_x) & (point_data[y_pos] == end_y)]
            i += 1
        except ValueError as e:
            print('线的始末点可能不在现有的点中\n', e)
    return arc_list
