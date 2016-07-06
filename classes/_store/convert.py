# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np

##########################
# convert
##########################


def idx_to_dict(net, _type, nodes_ID):
    """
    tp.classes.convert.net_to_turn_table 中的 get_node_link 函数的采用
    net的idx的版本，经过测试，发现效率没有显著提高(1000边):

    get_node_link : 10 loops, best of 3: 50.5 ms per loop
    idx_to_dict : 10 loops, best of 3: 46.9 ms per loop

    而且需要提供 idx, 所以暂时抛弃

    Parameters
    ----------
    net : net
    _type : {'start', 'end'}
    nodes_ID : set
    node_ID : set
        A set of nodes's ID which need to be counted.

    Returns
    -------
    dict :
        返回字典的键为 `node` 的 `ID`, 值为以 `node` 为起点/终点的所有
        道路的 `ID` 组成的列表.
    """
    data = net._data
    info_dict = {}
    if _type == 'start':
        idx = net.idx
        for ID in nodes_ID:
            foo1 = idx[ID - 1]
            foo2 = idx[ID]
            info_dict[ID] = data['ID'][foo1:foo2]
    elif _type == 'end':
        r_idx = net.r_idx
        trace = net.trace
        for ID in nodes_ID:
            foo1 = r_idx[ID - 1]
            foo2 = r_idx[ID]
            info_dict[ID] = data['ID'][trace[foo1:foo2]]
    return info_dict
