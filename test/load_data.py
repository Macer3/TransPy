# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
from transpy.readwrite.rw_txt import *
import transpy as tp
import os

# todo 现在还只有一个数据集，将来数据集很多的时候，应该有一种通用的加载数据的办法
# 得到当前脚本的绝对路径
path = os.path.split(os.path.realpath(__file__))[0]


def load_raw_test_data():
    data = load_txt_table(path + '/data/typical_type/street.asc',
                          names=['ID', 'LENGTH', 'DIR', 'capacity', 'AB_flow',
                                 'BA_flow', 'AB_speed', 'BA_speed',
                                 'AB_times',
                                 'BA_times', 'AB_v/c', 'BA_v/c'])
    point_data = load_point_geo_txt(path + '/data/typical_type/node.geo',
                                    ptype='LONG_LAT')
    line_data = load_line_geo_txt(path + '/data/typical_type/street.geo',
                                  ptype='LONG_LAT')
    link_data = tp.geo.build_point_line_connection(point_data,
                                                   line_data,
                                                   ptype='LONG_LAT')
    link_data = tp.merge_two_table(link_data, data)
    turn_table = load_txt_table(path + '\data\\typical_type\\turn_more.txt',
                                names=['ID', 'FROM', 'TO', 'DELAY'],
                                formats=['u2', 'u2', 'u2', 'f8'],
                                filing_values={'f': np.inf})
    matrix_table = load_txt_table(path + '\data\\typical_type\\matrix.txt',
                                  names=['O', 'D', 'flow'],
                                  formats=['u2', 'u2', 'f8'],
                                  fast_mode=True)
    matrix = tp.zero_matrix(9, 9)
    matrix.row_idx = matrix_table['O'][0::9]
    matrix.col_idx = matrix_table['D'][0:9]
    matrix._data = matrix_table['flow'].copy().reshape((9, 9))

    return point_data, line_data, link_data, turn_table, matrix


def load_test_data():
    point_data, line_data, link_data, turn_table, matrix = load_raw_test_data()
    node_table = tp.IDTable(point_data)
    link_table = tp.IDTable(link_data)
    turn_table = tp.IDGroupTable(turn_table)
    net = tp.Net(link_table,
                 fields=['ID', 'LENGTH', 'DIR', 'capacity',
                         'AB_flow', 'BA_flow', 'AB_speed',
                         'BA_speed', 'AB_times', 'BA_times', 'AB_v/c',
                         'BA_v/c'],
                 turn_table=turn_table)
    return node_table, link_table, turn_table, net, matrix


def load_assignment_result(name='all_or_nothing'):
    result = load_txt_table(path + '/data/typical_type/{}.txt'.format(name),
                            names=['ID', 'AB_FLOW', 'BA_FLOW'],
                            formats=['u2', 'f8', 'f8'])
    turn = load_txt_table(
        path + '/data/typical_type/{}_turn.txt'.format(name),
        names=['FROM', 'TO', 'ID', 'FLOW'],
        formats=['u2', 'u2', 'u2', 'f8'])
    return result, turn


if __name__ == '__main__':
    point_data, line_data, link_data, turn_table, matrix = load_raw_test_data()
