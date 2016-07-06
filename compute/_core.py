# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np
import transpy as tp
from transpy.compute.heap import FastUpdateBinaryHeap

ID_TYPE = tp.ID_TYPE
NONE = tp.NONE
INF = np.inf

def turn_dijikstra(idx, ID, end_node, weight, flag, source, target,
                    max_dist, max_node, turn_idx, from_link, to_link,
                    delay, dist, node_pred, arc_pred):
    """Dijkstra algorithm for the shortest DIR problem with turning delay.

    When take turning delay into consideration, nodes can not be used to
    label the searched part, because nodes may be reached more than once
    in some cases. So this algorithm maintains information about labels
    and distances of searched arcs, instead of nodes.

    The `ID` of arcs is not unique, two directions of one link have the
    same `ID`. So we use the row number(row position of an arc in Net._data)
    to identify and label each arc.

    Besides a binary heap written by Almar Klein is used to improve the
    performance.

    Parameters
    ----------
    idx : ndarray
        The idx array of net, ``net.idx``.
    ID : ndarray
        A field of Net, ``Net['ID']``.
    end_node : ndarray
        A field of Net, ``Net['END_NODE']``.
    weight : ndarray
        A field of Net, which would be seen as the weight of arcs.
        ``Net['LENGTH']`` or ``Net['TIME']`` ect.
    flag : ndarray
        A field of Net, ``Net['FLAG']``.
    source : int
        The source node's ID.
    target : int
        The target node's ID. If is 0, search all node.
    max_dist : float
        The algorithm will stop when the distance bigger than `max_dist`.
    max_node : int
        The algorithm will stop when the number of searched nodes reach
        the `max_node`(include source node). If is 0, search all nodes.
    turn_idx : ndarray
        The idx array of turn_table, ``turn_table.idx``.
    from_link : ndarray
        A field of turn_table, ``turn_table['FROM']``.
    to_link : ndarray
        A field of turn_table, ``turn_table['TO']``.
    delay : ndarray
        A field of turn_table, ``turn_table['DELAY']`` or you can specify.
    dist : ndarray
        A ndarray used to store the shortest distance from source node to
        each arc. It uses arc's row number to index, so the length of it
        should be same as ``Net._data``. And the initial value should be
        all INFs.
    node_pred : ndarray
        A ndarray used to store the node's preceding arc's row number. It
        uses node's ID to index, the length of it should be big enough to
        contain the biggest node ID. And initial value should be all NONEs.
    arc_pred : ndarray
        A ndarray used to store the arc's preceding arc's row number. It
        uses arc's row number to index, so the length of it should be same
        as ``Net._data``. And the initial value should be all NONEs.

    Note
    ----
    Arc's weight and turning-delay must be non negative, and there will be
    no warning or error raised when negative value occur.

    Not a Number (`nan`) in weight or turning-delay has the same effect of
    positive infinity, Just like no such arc or turns.
    """
    costs_heap = FastUpdateBinaryHeap(initial_capacity=128,
                                      max_reference=dist.shape[0])
    marker = np.zeros(node_pred.shape, np.uint8)
    max_turn_line = from_link.shape[0] - 1
    if max_node == 0:
        max_node = set(end_node).__len__()
    # If change algorithm to no-marker version, count = 0;
    count = 1
    start_l = idx[source - 1]
    end_l = idx[source]
    marker[source] = 1
    for l in range(start_l, end_l):
        n_dist = weight[l]
        if np.isfinite(n_dist):  # To prevent nan or inf push into heap
            dist[l] = n_dist
            costs_heap.push(n_dist, l)

    while costs_heap.count != 0:
        if count >= max_node:
            return

        c_dist, c_line = costs_heap.pop()
        if c_dist >= max_dist:
            return

        c_node = end_node[c_line]
        if node_pred[c_node] == NONE:
            node_pred[c_node] = c_line
            count += 1

        if c_node == target:
            return

        start_l = idx[c_node - 1]
        end_l = idx[c_node]
        c_flag = flag[c_line]

        # If with turning delay
        if c_flag:
            c_link = ID[c_line]
            # The first line_num of this arc in turn_table.
            line = turn_idx[c_node] - c_flag
            for l in range(start_l, end_l):
                n_link = ID[l]
                if from_link[line] != c_link:
                    n_dist = c_dist + weight[l]
                elif to_link[line] != n_link:
                    n_dist = c_dist + weight[l]
                else:
                    n_dist = c_dist + weight[l] + delay[line]
                    if line < max_turn_line:
                        line += 1

                n_node = end_node[l]
                if marker[n_node]:
                    continue
                if n_dist < dist[l]:
                    arc_pred[l] = c_line
                    dist[l] = n_dist
                    costs_heap.push_if_lower(n_dist, l)

        else:
            # When a incoming arc has no turning delay to any outgoing arcs
            # of it's node, this node will not be re-reached, so mark it to
            # avoid re-reach for speed-up.
            marker[c_node] = 1
            for l in range(start_l, end_l):
                n_node = end_node[l]
                if marker[n_node]:
                    continue
                n_dist = c_dist + weight[l]

                if n_dist < dist[l]:
                    arc_pred[l] = c_line
                    dist[l] = n_dist
                    costs_heap.push_if_lower(n_dist, l)



def c_all_or_nothing(sources, targets, matrix, idx, ID, end_node, weight, flag,
                     turn_idx, from_link, to_link, delay, dist, node_pred,
                     arc_pred, arcs_flow, a, b, turns_flow):
    """

    Parameters
    ----------
    sources :
    targets :
    matrix :
    idx :
    ID :
    end_node :
    weight :
    flag :
    turn_idx :
    from_link :
    to_link :
    delay :
    dist :
    node_pred :
    arc_pred :
    arcs_flow :
    a :
    b :
    turns_flow :

    Returns
    -------

    """
    if a.shape[0] == 1:  # If no need to count turning flow.
        update_flow = update_arcs_flow
    else:  # If need to count turning flow.
        update_flow = update_arcs_turns_flow

    for i in range(sources.shape[0]):
        dist[:] = INF
        source = sources[i]
        node_pred[:] = NONE
        arc_pred[:] = NONE
        turn_dijikstra(idx, ID, end_node, weight, flag, source, 0, INF, 0,
                        turn_idx, from_link, to_link, delay, dist, node_pred,
                        arc_pred)
        for j in range(targets.shape[0]):
            target = targets[j]
            if source == target:
                continue
            out_arc = node_pred[target]
            if out_arc == NONE:
                print('No DIR from {} to {}'.format(source, target))
                continue
            flow = matrix[i, j]
            update_flow(flow, arc_pred, out_arc, arcs_flow, a, b, turns_flow)


def c_single_all_or_nothing(source, targets, matrix, idx, ID, end_node,
                            weight, flag, turn_idx, from_link, to_link,
                            delay, dist, node_pred, arc_pred, arcs_flow,
                            a, b, turns_flow):
    if a.shape[0] == 1:  # If no need to count turning flow.
        update_flow = update_arcs_flow
    else:  # If need to count turning flow.
        update_flow = update_arcs_turns_flow

    turn_dijikstra(idx, ID, end_node, weight, flag, source, 0, INF, 0,
                    turn_idx, from_link, to_link, delay, dist, node_pred,
                    arc_pred)
    for i in range(targets.shape[0]):
        target = targets[i]
        if source == target:
            continue
        out_arc = node_pred[target]
        if out_arc == NONE:
            print('No DIR from {} to {}'.format(source, target))
            continue
        flow = matrix[i]
        update_flow(flow, arc_pred, out_arc, arcs_flow, a, b, turns_flow)


def update_arcs_flow(flow, arc_pred, out_arc, arcs_flow, a, b, turns_flow):
    while out_arc != NONE:
        arcs_flow[out_arc] += flow
        out_arc = arc_pred[out_arc]


def update_arcs_turns_flow(flow, arc_pred, out_arc, arcs_flow, a, b,
                           turns_flow):
    arcs_flow[out_arc] += flow
    in_arc = arc_pred[out_arc]
    while in_arc != NONE:
        arcs_flow[in_arc] += flow
        a_line = a[in_arc]
        if a_line != NONE:
            b_line = b[out_arc]
            turns_flow[a_line + b_line] += flow
        out_arc = in_arc
        in_arc = arc_pred[out_arc]