# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
from transpy.readwrite.rw_txt import *
import transpy as tp
import os
from transpy.compute.assignment import all_or_nothing, user_equilibrium, \
    AssignConfig
import numpy as np

path = "D:\Documents\PythonS\\transpy\\test\\transpy\\test\data\Weihai_City\\"


def load_raw_test_data():
    line_table = load_txt_table(path + 'street.txt',
                                names=['ID', 'LENGTH', 'DIR', 'Layer',
                                       'Handle', 'times', 'speed', 'capacity',
                                       'AB_flow', 'BA_flow', 'names'],
                                formats=['i4', 'f4', 'u1', 'U1', 'i4', 'f8',
                                         'i4', 'i4', 'i4', 'i4', 'U16'],
                                encoding='gbk')
    accurate_line_data = load_bin(path + 'line.bin')
    line_table['times'] = accurate_line_data['time']
    del accurate_line_data

    point_table = load_txt_table(path + 'Endpoints.txt',
                                 names=['ID', 'LONG', 'LAT', 'index'],
                                 encoding='gbk')

    point_data = load_point_geo_txt(path + 'node.geo',
                                    ptype='LONG_LAT', encoding='gbk')

    point_table.sort(order=['ID'])
    point_data.sort(order=['ID'])
    point_table['LONG'] = point_data['LONG']
    point_table['LAT'] = point_data['LAT']

    line_data = load_line_geo_txt(path + 'street.geo',
                                  ptype='LONG_LAT', encoding='gbk')
    link_data = tp.geo.build_point_line_connection(point_data,
                                                   line_data,
                                                   ptype='LONG_LAT')
    link_data = tp.merge_two_table(link_data, line_table)

    turn_table = load_txt_table(path + '\\turn.txt',
                                names=['ID', 'FROM', 'TO', 'DELAY'],
                                formats=['u2', 'u2', 'u2', 'f8'],
                                filing_values={'f': np.inf})
    matrix_table = load_bin(path + 'matrix.bin')
    matrix = tp.Matrix(matrix_table['pre'].copy().reshape((50, 50)))
    matrix.row_idx = matrix_table['O'][0::50]
    matrix.col_idx = matrix_table['D'][0:50]
    matrix._data = np.asarray(matrix._data, dtype=np.float64)

    return point_data, line_data, link_data, turn_table, matrix


def load_test_data():
    point_data, line_data, link_data, turn_table, matrix = load_raw_test_data()
    node_table = tp.IDTable(point_data)
    link_table = tp.IDTable(link_data)
    if turn_table is not None:
        turn_table = tp.IDGroupTable(turn_table)
    net = tp.Net(link_table,
                 fields=['ID', 'LENGTH', 'DIR', 'capacity', 'times',
                         'AB_flow', 'BA_flow'],
                 turn_table=turn_table)
    return node_table, link_table, turn_table, net, matrix


cfg = AssignConfig()
cfg.method = 'UE'
cfg.time_field = 'times'
cfg.capacity_field = 'capacity'
cfg.convergence = 0.001
cfg.max_iteration = 100
cfg.preload_field = 'flow'
cfg.turn_delay_type = 'all'
cfg.focus_nodes = [9]
cfg.print_frequency = 2
cfg.focus_nodes = None

_, link_table, _, net, matrix = load_test_data()
arcs_flow, turns_flow, summary= user_equilibrium(net, matrix, link_table,
                                                  cfg)
