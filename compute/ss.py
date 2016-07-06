# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
from transpy.gui.test_double import road
from transpy.gui.test_plot import load_test_data
from transpy.gui.test_ss import draw_flow
from transpy.compute.assignment import *
import transpy as tp

# 导入第三方模块
from ipywidgets import interact
import matplotlib.pyplot as plt

# 导入数据
point_table, line_data, node_table, link_table, turn_table, net, matrix = load_test_data()

# 交通分配配置
cfg = AssignConfig()
cfg.method = 'UE'
cfg.time_field = 'times'
cfg.capacity_field = 'capacity'
cfg.convergence = 0.001    # 收敛精度
cfg.max_iteration = 100    # 最大迭代次数
cfg.preload_field = 'flow'
cfg.turn_delay_type = 'all'
cfg.print_frequency = 1

timeit link_flow, turns_flow, summary = user_equilibrium(net, matrix, link_table,cfg)
