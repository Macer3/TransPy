# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
from transpy.test.load_data import load_test_data, load_assignment_result
from transpy.compute._core import all_or_nothing, user_equilibrium, assignment_config
import numpy as np
import nose.tools as nt

NULL = 65535

_, link_table, _, net, matrix = load_test_data()

cfg = assignment_config()
cfg.method = 'UE'
cfg.time_field = 'times'
cfg.capacity_field = 'capacity'
cfg.preload_field='flow'
cfg.convergence = 0.001
cfg.focus_nodes = 'all'


def test_all_or_nothing():
    result_arc, result_turn = load_assignment_result('AON')
    arcs_flow, turns_flow = all_or_nothing(net, matrix, link_table, cfg)

    arcs_flow.sort(order=['ID'])
    np.testing.assert_array_equal(result_arc['AB_FLOW'], arcs_flow['AB_FLOW'],
                                  'all_or_nothing link flows wrong.')
    np.testing.assert_array_equal(result_arc['BA_FLOW'], arcs_flow['BA_FLOW'],
                                  'all_or_nothing link flows wrong.')

    result_turn.sort(order=['ID', 'FROM', 'TO'])
    turns_flow = turns_flow[turns_flow['FLOW'] != 0]
    j = 0
    turn_shape = turns_flow.shape[0]
    for i in range(result_turn.shape[0]):
        if result_turn[['ID', 'FROM', 'TO']][i] == turns_flow[['ID', 'FROM', 'TO']][j]:
            nt.assert_almost_equals(result_turn[i]['FLOW'],
                                    turns_flow[j]['FLOW'],
                                    'all_or_nothing turns flows wrong.')
            if j < turn_shape:
                j += 1
    print("Total {} turns_flow, {} right".format(turn_shape,j))


def test_ue():
    summary, arcs_flow, turns_flow = user_equilibrium(net, matrix, link_table, cfg)
    return summary, arcs_flow,turns_flow

test_ue()
#test_all_or_nothing()