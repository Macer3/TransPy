# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""

import numpy as np
from transpy.test.load_data import load_raw_test_data
import transpy as tp
import os
from transpy.classes.convert import *
import nose.tools as nt
from transpy.compute.shortest_way import single_source_shortest_way

point_data, line_data, link_data, turn_table, _ = load_raw_test_data()
link_table = tp.IDTable(link_data)
node_table = tp.IDTable(point_data)
turn_table = tp.IDGroupTable(turn_table)
net = tp.Net(link_table,
             fields=['ID', 'LENGTH', 'DIR', 'capacity',
                     'AB_flow', 'BA_flow', 'AB_speed',
                     'BA_speed', 'AB_times', 'BA_times', 'AB_v/c', 'BA_v/c'],
             turn_table=turn_table)


def test_net_to_turn_table(net):
    turning_table = net_to_turn_table(net, exclude=False)
    nt.assert_equal(turn_table.shape[0], 131,
                    "turning_table's shape Wrong")
    return turning_table


def test_update_net_flag(net, turning_table):
    update_net_flag(net, turning_table)
    np.testing.assert_equal(net._data[15:19]['FLAG'],
                            np.array([4, 5, 6, 2], np.uint8))


if __name__ == '__main__':
    # a = test_net_to_turn_table(net)
    # test_update_net_flag(net, turn_table)
    # print(a[0:13])
    dist, path = single_source_shortest_way(net, 'LENGTH', 26,
                                            return_type='node')
    print(path)
    print(dist)
