# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
from transpy.compute.heap import FastUpdateBinaryHeap
import numpy as np

cimport numpy as np
cimport cython
from transpy.compute.heap cimport FastUpdateBinaryHeap

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

ITYPE = np.int32
ctypedef np.int32_t ITYPE_t

# currently ID is uint16
UTYPE16 = np.uint16
ctypedef np.uint16_t UTYPE16_t

UTYPE8 = np.uint8
ctypedef np.uint8_t UTYPE8_t

cdef UTYPE16_t NONE = tp.NONE
cdef DTYPE_t INF = np.inf


def single_source_shortest_way(net, weight, source, target=None,
                               turn_delay_type='all', max_dist=INF,
                               max_node=0, return_type='link'):
    """
    Parameters
    ----------
    net : Net
        用于计算最短路的网络.
    source : int
        起始节点的 `ID`.
    weight : str
        用于计算的最短路的域名.
    target : int, optional
        目标节点的 `ID`, 若有指明, 搜寻到目标节点后算法即停止, Default: 搜索
        所有节点.
    turn_delay_type : {'no','only_ban','all'}, optional
        计算转向延误的方式, 为 'no' 时不计算转向延误, 'ban' 时仅考虑禁止转
        向, 为 'all' 时计算转向表中的所有转向. Default: 'all'.
    max_dist : float, optional
        The algorithm will stop when the distance bigger than `max_dist`.
        Default: INF.
    max_node : int, optional
        The algorithm will stop when the number of searched nodes reach
        the `max_node`(include source node). If is 0, search all nodes.
        Default: 0.
    return_type : {'pred','link','node'}, optional
        返回值的类型, 为 'DIR' 时返回最距离字典与最短路径字典, 为 'pred' 时
        返回最距离字典与前向节点数组(predecessors), 为 'both' 时返回最距离字
        典,最短路径字典与前向节点数组. Default: 'DIR'.
    """
    # First prepare basic data
    flag, turn_idx, from_link, to_link, delay, dist, node_pred, arc_pred = \
        prepare_data(net, turn_delay_type)

    if target is None:
        target = 0
    data = net._data
    link_id = data['ID']
    weight = np.asarray(data[weight], np.float64)

    # Call inner function find shortest DIR
    _turn_dijikstra(net.idx, link_id, data['END_NODE'], weight,
                    flag, source, target, max_dist, max_node,
                    turn_idx, from_link, to_link, delay, dist,
                    node_pred, arc_pred)

    # According return_type, return corresponding value
    if return_type == 'pred':
        return dist, node_pred, arc_pred

    r_dist = {}
    path = {}
    if return_type == 'link':
        if target != 0:
            if node_pred[target] != NONE:
                r_dist[target] = dist[node_pred[target]]
                path[target] = pred_to_link(arc_pred, node_pred, link_id,
                                            target)
        else:
            for i in range(node_pred.shape[0]):
                if node_pred[i] != NONE:
                    r_dist[i] = dist[node_pred[i]]
                    path[i] = pred_to_link(arc_pred, node_pred, link_id, i)

    elif return_type == 'node':
        start_node = data['START_NODE']
        if target != 0:
            if node_pred[target] != NONE:
                r_dist[target] = dist[node_pred[target]]
                path[target] = pred_to_node(arc_pred, node_pred, start_node,
                                            target)
        else:
            for i in range(node_pred.shape[0]):
                if node_pred[i] != NONE:
                    r_dist[i] = dist[node_pred[i]]
                    path[i] = pred_to_node(arc_pred, node_pred, start_node, i)

    else:
        raise ValueError("Wrong return_type, use 'pred', 'link' or 'node'")

    return r_dist, path


def pred_to_node(arc_pred, node_pred, start_node, target):
    """Get the node-DIR from source node to target node.

    Parameters
    ----------
    arc_pred : ndarray
        A ndarray stores the arc's preceding arc's row number, which can
        calculated by `_turn_dijikstra()`.
    node_pred : ndarray
        A ndarray stores the node's preceding arc's row number, which can
        calculated by `_turn_dijikstra()`.
    start_node : ndarray
        A field of Net, ``Net['START_NODE']``.
    target : int
        The target node's ID.

    Returns
    -------
    list
        A list stores the node's ID from source to target. If no DIR
        from source to target, the list is [].

    See Also
    --------
    pred_to_link
    """
    pred_line = node_pred[target]
    if pred_line == NONE:
        return []
    path = [target]
    while pred_line != NONE:
        path.append((start_node[pred_line]))
        pred_line = arc_pred[pred_line]
    path.reverse()
    return path


def pred_to_link(arc_pred, node_pred, link_id, target):
    """Get the link-DIR from source node to target node.

    Parameters
    ----------
    arc_pred : ndarray
        A ndarray stores the arc's preceding arc's row number, which can
        calculated by `_turn_dijikstra()`.
    node_pred : ndarray
        A ndarray stores the node's preceding arc's row number, which can
        calculated by `_turn_dijikstra()`.
    link_id : ndarray
        A field of Net, ``Net['ID']``.
    target : int
        The target node's ID.

    Returns
    -------
    list
        A list stores the link's ID from source to target. If no DIR
        from source to target, the list is [].

    See Also
    --------
    pred_to_node
    """
    path = []
    pred_line = node_pred[target]
    while pred_line != NONE:
        path.append(link_id[pred_line])
        pred_line = arc_pred[pred_line]
    path.reverse()
    return path


def prepare_data(net, turn_delay_type):
    """
    """
    if net.turn_table is None:
        turn_idx = from_link = to_link = np.zeros((1,), np.uint16)
        delay = np.zeros((1,), np.float64)
    else:
        turn_idx = net.turn_table.idx
        from_link = net.turn_table['FROM']
        to_link = net.turn_table['TO']
        delay = net.turn_table['DELAY']

    data = net._data
    if turn_delay_type == 'no':
        flag = np.zeros(data.shape, np.uint8)
    elif turn_delay_type == 'only_ban':
        delay = net.turn_table['DELAY'].copy()
        delay[delay != INF] = 0
        flag = data['FLAG']
    elif turn_delay_type == 'all':
        flag = data['FLAG']
    else:
        raise ValueError("Wrong turn_delay_type, use 'no','only_ban'"
                         " or 'all'")

    link_num = data.shape[0]
    node_num = net.r_idx.shape[0]
    dist = np.full((link_num,), np.inf, np.float64)
    node_pred = np.full((node_num,), NONE, ID_TYPE)
    arc_pred = np.full((link_num,), NONE, ID_TYPE)

    return (flag, turn_idx, from_link, to_link, delay,
            dist, node_pred, arc_pred)
