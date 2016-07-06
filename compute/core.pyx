# -*- python -*-
"""Fast network analyze algorithm written in Cython.

Main interface includes ``turn_dijikstra``, ``c_all_or_nothing`` and 
``c_single_all_or_nothing``

Author: Zhanhong Cheng 2016
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

cdef UTYPE16_t NONE = 65535
cdef DTYPE_t INF = np.inf

@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _turn_dijikstra(np.ndarray[UTYPE16_t, ndim=1] idx, 
                     np.ndarray[UTYPE16_t, ndim=1] ID, 
                     np.ndarray[UTYPE16_t, ndim=1] end_node, 
                     np.ndarray[DTYPE_t, ndim=1] weight, 
                     np.ndarray[UTYPE8_t, ndim=1] flag, 
                     UTYPE16_t source, 
                     UTYPE16_t target,
                     float max_dist,
                     UTYPE16_t max_node,
                     np.ndarray[UTYPE16_t, ndim=1] turn_idx,
                     np.ndarray[UTYPE16_t, ndim=1] from_link,
                     np.ndarray[UTYPE16_t, ndim=1] to_link,
                     np.ndarray[DTYPE_t, ndim=1] delay, 
                     np.ndarray[DTYPE_t, ndim=1] dist, 
                     np.ndarray[UTYPE16_t, ndim=1] node_pred, 
                     np.ndarray[UTYPE16_t, ndim=1] arc_pred):
    """The inner c-method for Dijkstra algorithm with turning delay.

    Parameters see `turn_dijikstra`

    See Also
    --------
    turn_dijikstra
    """
    cdef DTYPE_t n_dist, c_dist = 0
    cdef UTYPE16_t c_node, n_node, l, start_l, end_l, c_link, n_link, c_line, count
    cdef UTYPE16_t line, max_turn_line = from_link.shape[0] - 1
    cdef UTYPE8_t c_flag
    cdef FastUpdateBinaryHeap costs_heap = FastUpdateBinaryHeap(
                            initial_capacity=128, max_reference=dist.shape[0])
    cdef np.ndarray[UTYPE8_t, ndim=1] marker = np.zeros(node_pred.shape[0], np.uint8)
    

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
            costs_heap.push_fast(n_dist, l)

    while costs_heap.count != 0:
        
        if count >= max_node:
            return
        
        c_dist = costs_heap.pop_fast()
        c_line = costs_heap._popped_ref
        if c_dist >= max_dist:
            return

        c_node = end_node[c_line]
        # second time reach this node will not be counted
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
                    # prevent out of bound
                    if line < max_turn_line:
                        line += 1

                n_node = end_node[l]
                if marker[n_node]:
                    continue
                if n_dist < dist[l]:
                    arc_pred[l] = c_line
                    dist[l] = n_dist
                    costs_heap.push_if_lower_fast(n_dist, l)

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
                    costs_heap.push_if_lower_fast(n_dist, l)


@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _c_all_or_nothing(np.ndarray[UTYPE16_t, ndim=1] sources, 
                     np.ndarray[UTYPE16_t, ndim=1] targets,
                     np.ndarray[DTYPE_t, ndim=2] matrix, 
                     np.ndarray[UTYPE16_t, ndim=1] idx, 
                     np.ndarray[UTYPE16_t, ndim=1] ID, 
                     np.ndarray[UTYPE16_t, ndim=1] end_node, 
                     np.ndarray[DTYPE_t, ndim=1] weight, 
                     np.ndarray[UTYPE8_t, ndim=1] flag,
                     np.ndarray[UTYPE16_t, ndim=1] turn_idx, 
                     np.ndarray[UTYPE16_t, ndim=1] from_link, 
                     np.ndarray[UTYPE16_t, ndim=1] to_link, 
                     np.ndarray[DTYPE_t, ndim=1] delay, 
                     np.ndarray[DTYPE_t, ndim=1] dist, 
                     np.ndarray[UTYPE16_t, ndim=1] node_pred,
                     np.ndarray[UTYPE16_t, ndim=1] arc_pred, 
                     np.ndarray[DTYPE_t, ndim=1] arcs_flow, 
                     np.ndarray[UTYPE16_t, ndim=1] a, 
                     np.ndarray[UTYPE16_t, ndim=1] b, 
                     np.ndarray[DTYPE_t, ndim=1] turns_flow):
    """The inner c-method for All_or_Nothing assignment.

    Parameters see `c_all_or_nothing`

    See Also
    --------
    c_all_or_nothing
    """
    cdef UTYPE16_t i, j, source, target, out_arc, max_node
    cdef DTYPE_t flow
    if a.shape[0] == 1:  # If no need to count turning flow.
        update_flow = update_arcs_flow
    else:  # If need to count turning flow.
        update_flow = update_arcs_turns_flow
    max_node = set(end_node).__len__()

    for i in range(sources.shape[0]):
        dist[:] = INF
        source = sources[i]
        node_pred[:] = NONE
        arc_pred[:] = NONE
        _turn_dijikstra(idx, ID, end_node, weight, flag, source, 0, INF, 
                        max_node, turn_idx, from_link, to_link, delay, dist, 
                        node_pred, arc_pred)
        for j in range(targets.shape[0]):
            target = targets[j]
            if source == target:
                continue
            out_arc = node_pred[target]
            if out_arc == NONE:
                Warning('No path from {} to {}'.format(source, target))
                continue
            flow = matrix[i, j]
            update_flow(flow, arc_pred, out_arc, arcs_flow, a, b, turns_flow)


@cython.boundscheck(False)
@cython.wraparound(False)
cdef void _c_single_all_or_nothing(UTYPE16_t source, 
                            np.ndarray[UTYPE16_t, ndim=1] targets, 
                            np.ndarray[DTYPE_t, ndim=1] matrix, 
                            np.ndarray[UTYPE16_t, ndim=1] idx, 
                            np.ndarray[UTYPE16_t, ndim=1] ID, 
                            np.ndarray[UTYPE16_t, ndim=1] end_node,
                            np.ndarray[DTYPE_t, ndim=1] weight, 
                            np.ndarray[UTYPE8_t, ndim=1] flag, 
                            np.ndarray[UTYPE16_t, ndim=1] turn_idx, 
                            np.ndarray[UTYPE16_t, ndim=1] from_link, 
                            np.ndarray[UTYPE16_t, ndim=1] to_link,
                            np.ndarray[DTYPE_t, ndim=1] delay, 
                            np.ndarray[DTYPE_t, ndim=1] dist, 
                            np.ndarray[UTYPE16_t, ndim=1] node_pred, 
                            np.ndarray[UTYPE16_t, ndim=1] arc_pred, 
                            np.ndarray[DTYPE_t, ndim=1] arcs_flow,
                            np.ndarray[UTYPE16_t, ndim=1] a, 
                            np.ndarray[UTYPE16_t, ndim=1] b, 
                            np.ndarray[DTYPE_t, ndim=1] turns_flow):
    """The inner c-method for All_or_Nothing assignment from 
    single source node to other nodes.

    Parameters see `c_single_all_or_nothing`

    See Also
    --------
    c_single_all_or_nothing
    """
    cdef UTYPE16_t i, target, out_arc
    cdef DTYPE_t flow
    if a.shape[0] == 1:  # If no need to count turning flow.
        update_flow = update_arcs_flow
    else:  # If need to count turning flow.
        update_flow = update_arcs_turns_flow

    _turn_dijikstra(idx, ID, end_node, weight, flag, source, 0, INF, 0,
                    turn_idx, from_link, to_link, delay, dist, node_pred,
                    arc_pred)
    for i in range(targets.shape[0]):
        target = targets[i]
        if source == target:
            continue
        out_arc = node_pred[target]
        if out_arc == NONE:
            Warning('No path from {} to {}'.format(source, target))
            continue
        flow = matrix[i]
        update_flow(flow, arc_pred, out_arc, arcs_flow, a, b, turns_flow)


@cython.boundscheck(False)
@cython.wraparound(False)
cdef void update_arcs_flow(DTYPE_t flow,
                      np.ndarray[UTYPE16_t, ndim=1] arc_pred,
                      UTYPE16_t out_arc, 
                      np.ndarray[DTYPE_t, ndim=1] arcs_flow, 
                      np.ndarray[UTYPE16_t, ndim=1] a, 
                      np.ndarray[UTYPE16_t, ndim=1] b, 
                      np.ndarray[DTYPE_t, ndim=1] turns_flow):
    while out_arc != NONE:
        arcs_flow[out_arc] += flow
        out_arc = arc_pred[out_arc]


@cython.boundscheck(False)
@cython.wraparound(False)
cdef void update_arcs_turns_flow(DTYPE_t flow,
                                np.ndarray[UTYPE16_t, ndim=1] arc_pred,
                                UTYPE16_t out_arc, 
                                np.ndarray[DTYPE_t, ndim=1] arcs_flow, 
                                np.ndarray[UTYPE16_t, ndim=1] a, 
                                np.ndarray[UTYPE16_t, ndim=1] b, 
                                np.ndarray[DTYPE_t, ndim=1] turns_flow):
    """Update arcs and turns flow during the assignment.

    Parameters
    ----------
    flow : float
        The traffic flow of a certain OD pair in OD matrix.
    """
    cdef UTYPE16_t in_arc, a_line, b_line
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

def turn_dijikstra(np.ndarray[UTYPE16_t, ndim=1] idx, 
                     np.ndarray[UTYPE16_t, ndim=1] ID, 
                     np.ndarray[UTYPE16_t, ndim=1] end_node, 
                     np.ndarray[DTYPE_t, ndim=1] weight, 
                     np.ndarray[UTYPE8_t, ndim=1] flag, 
                     UTYPE16_t source, 
                     UTYPE16_t target,
                     float max_dist,
                     UTYPE16_t max_node,
                     np.ndarray[UTYPE16_t, ndim=1] turn_idx,
                     np.ndarray[UTYPE16_t, ndim=1] from_link,
                     np.ndarray[UTYPE16_t, ndim=1] to_link,
                     np.ndarray[DTYPE_t, ndim=1] delay, 
                     np.ndarray[DTYPE_t, ndim=1] dist, 
                     np.ndarray[UTYPE16_t, ndim=1] node_pred, 
                     np.ndarray[UTYPE16_t, ndim=1] arc_pred):
    """Dijkstra algorithm for the shortest path problem with turning delay.

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
    positive infinity, Just like no such arc or turns."""
    _turn_dijikstra (idx, ID, end_node, weight, flag, source, target,
                     max_dist, max_node, turn_idx, from_link, to_link,
                     delay, dist, node_pred, arc_pred)

def c_all_or_nothing(np.ndarray[UTYPE16_t, ndim=1] sources, 
                     np.ndarray[UTYPE16_t, ndim=1] targets,
                     np.ndarray[DTYPE_t, ndim=2] matrix, 
                     np.ndarray[UTYPE16_t, ndim=1] idx, 
                     np.ndarray[UTYPE16_t, ndim=1] ID, 
                     np.ndarray[UTYPE16_t, ndim=1] end_node, 
                     np.ndarray[DTYPE_t, ndim=1] weight, 
                     np.ndarray[UTYPE8_t, ndim=1] flag,
                     np.ndarray[UTYPE16_t, ndim=1] turn_idx, 
                     np.ndarray[UTYPE16_t, ndim=1] from_link, 
                     np.ndarray[UTYPE16_t, ndim=1] to_link, 
                     np.ndarray[DTYPE_t, ndim=1] delay, 
                     np.ndarray[DTYPE_t, ndim=1] dist, 
                     np.ndarray[UTYPE16_t, ndim=1] node_pred,
                     np.ndarray[UTYPE16_t, ndim=1] arc_pred, 
                     np.ndarray[DTYPE_t, ndim=1] arcs_flow, 
                     np.ndarray[UTYPE16_t, ndim=1] a, 
                     np.ndarray[UTYPE16_t, ndim=1] b, 
                     np.ndarray[DTYPE_t, ndim=1] turns_flow):
    """All_or_Nothing assignment.

    Parameters
    ----------
    sources : ndarray
        A 1d ndarray of sources's ID.
    targets : ndarray
        A 1d ndarray of targets's ID.
    matrix : ndarray
        An OD matrix of 2d ndarray.
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
    arcs_flow : ndarray
        The ndarray to be filled with the acrs's flow.
    a, b : ndarray
        Runtime index array to fast fill turns_flow. In here the initial
        input value should be all NONEs.
    turns_flow : ndarray
        The ndarray to be fill with the acrs's flow.

    See Also
    --------
    c_single_all_or_nothing
    """
    _c_all_or_nothing(sources, targets, matrix, idx, ID, end_node, weight, 
                      flag, turn_idx, from_link, to_link, delay, dist, 
                      node_pred, arc_pred, arcs_flow, a, b, turns_flow)

def c_single_all_or_nothing(UTYPE16_t source, 
                            np.ndarray[UTYPE16_t, ndim=1] targets, 
                            np.ndarray[DTYPE_t, ndim=1] matrix, 
                            np.ndarray[UTYPE16_t, ndim=1] idx, 
                            np.ndarray[UTYPE16_t, ndim=1] ID, 
                            np.ndarray[UTYPE16_t, ndim=1] end_node,
                            np.ndarray[DTYPE_t, ndim=1] weight, 
                            np.ndarray[UTYPE8_t, ndim=1] flag, 
                            np.ndarray[UTYPE16_t, ndim=1] turn_idx, 
                            np.ndarray[UTYPE16_t, ndim=1] from_link, 
                            np.ndarray[UTYPE16_t, ndim=1] to_link,
                            np.ndarray[DTYPE_t, ndim=1] delay, 
                            np.ndarray[DTYPE_t, ndim=1] dist, 
                            np.ndarray[UTYPE16_t, ndim=1] node_pred, 
                            np.ndarray[UTYPE16_t, ndim=1] arc_pred, 
                            np.ndarray[DTYPE_t, ndim=1] arcs_flow,
                            np.ndarray[UTYPE16_t, ndim=1] a, 
                            np.ndarray[UTYPE16_t, ndim=1] b, 
                            np.ndarray[DTYPE_t, ndim=1] turns_flow):
    """All_or_Nothing assignment from single source node to other nodes.

    Parameters
    ----------
    source : int
        The source's ID.
    targets : ndarray
        A 1d ndarray of targets's ID.
    matrix : ndarray
        An OD matrix of 1d ndarray.
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
    arcs_flow : ndarray
        The ndarray to be filled with the acrs's flow.
    a, b : ndarray
        Runtime index array to fast fill turns_flow. In here the initial
        input value should be all NONEs.
    turns_flow : ndarray
        The ndarray to be fill with the acrs's flow.

    See Also
    --------
    c_all_or_nothing
    """
    _c_single_all_or_nothing(source, targets, matrix, idx, ID, end_node, weight, 
                             flag, turn_idx, from_link, to_link, delay, dist, 
                             node_pred, arc_pred, arcs_flow, a, b, turns_flow)