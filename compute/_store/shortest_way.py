# 这个版本， 在heap和dist的判断和更新上有所改进，也许在cython里会更快吧
def _turn_dijikstra2(idx, ID, end_node, weight, flag, source, target,
                     max_dist,
                     max_node, turn_idx, _from, _to, delay, dist, node_pred,
                     arc_pred):
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
    _from : ndarray
        A field of turn_table, ``turn_table['FROM']``.
    _to : ndarray
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
        contain the biggest node ID. And initial value should be all NULLs.
    arc_pred : ndarray
        A ndarray used to store the arc's preceding arc's row number. It
        uses arc's row number to index, so the length of it should be same
        as ``Net._data``. And the initial value should be all NULLs.

    Note
    ----
    Arc's weight and turning delay must be non negative.
    """
    costs_heap = FastUpdateBinaryHeap(initial_capacity=128,
                                      max_reference=dist.shape[0])
    if max_node == 0:
        max_node = set(end_node).__len__()

    count = 1
    start_l = idx[source - 1]
    end_l = idx[source]
    for l in range(start_l, end_l):
        n_dist = weight[l]
        dist[l] = n_dist
        costs_heap.push(n_dist, l)

    while costs_heap.count != 0:
        if count >= max_node:
            return
        c_dist, c_line = costs_heap.pop()
        c_node = end_node[c_line]
        dist[c_line] = c_dist

        if c_dist >= max_dist:
            return
        if c_node == source:
            continue
        if node_pred[c_node] == NULL:   # 如果第一次pop到该顶点
            node_pred[c_node] = c_line
            count += 1

        if c_node == target:
            return

        c_flag = flag[c_line]
        start_l = idx[c_node - 1]
        end_l = idx[c_node]

        if c_flag:  # When with turning delay
            c_link = ID[c_line]
            line = turn_idx[c_node] - c_flag  # corresponding delay line_num
            for l in range(start_l, end_l):
                n_link = ID[l]
                try:
                    if _from[line] != c_link:
                        n_dist = c_dist + weight[l]
                    elif _to[line] != n_link:
                        n_dist = c_dist + weight[l]
                    else:
                        n_dist = c_dist + weight[l] + delay[line]
                        line += 1
                except:  # todo 这里不太好，最好还是把turn_table 的最后一行变成NULL
                    n_dist = c_dist + weight[l]

                if n_dist < dist[l]:
                    if costs_heap.push_if_lower(n_dist, l):
                        arc_pred[l] = c_line

        else:  # When no turning delay
            for l in range(start_l, end_l):
                n_dist = c_dist + weight[l]

                if n_dist < dist[l]:
                    if costs_heap.push_if_lower(n_dist, l):
                        arc_pred[l] = c_line

# 没有 marker 的版本，对于所有交叉口都有转向延误的路网会更快一点点， 但
# 实际上往往不会给每个交叉口都设置延误，那样太麻烦，综上，软件中统一采用
# 了有 marker 的版本。
def _turn_dijikstra(idx, ID, end_node, weight, flag, source, target, max_dist,
                    max_node, turn_idx, _from, _to, delay, dist, node_pred,
                    arc_pred):
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
    _from : ndarray
        A field of turn_table, ``turn_table['FROM']``.
    _to : ndarray
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
        contain the biggest node ID. And initial value should be all NULLs.
    arc_pred : ndarray
        A ndarray used to store the arc's preceding arc's row number. It
        uses arc's row number to index, so the length of it should be same
        as ``Net._data``. And the initial value should be all NULLs.

    Note
    ----
    Arc's weight and turning delay must be non negative.
    """
    costs_heap = FastUpdateBinaryHeap(initial_capacity=128,
                                      max_reference=dist.shape[0])
    if max_node == 0:
        max_node = set(end_node).__len__()

    count = 0
    start_l = idx[source - 1]
    end_l = idx[source]
    for l in range(start_l, end_l):
        n_dist = weight[l]
        dist[l] = n_dist
        costs_heap.push(n_dist, l)

    while costs_heap.count != 0:
        if count >= max_node:
            return
        c_dist, c_line = costs_heap.pop()
        c_node = end_node[c_line]

        if c_dist >= max_dist:
            return

        if node_pred[c_node] == NONE:  # 如果第一次pop到该顶点
            node_pred[c_node] = c_line
            count += 1
        if c_node == target:
            return

        c_flag = flag[c_line]
        start_l = idx[c_node - 1]
        end_l = idx[c_node]

        if c_flag:  # When with turning delay
            c_link = ID[c_line]
            line = turn_idx[c_node] - c_flag  # corresponding delay line_num
            for l in range(start_l, end_l):
                n_link = ID[l]
                try:
                    if _from[line] != c_link:
                        n_dist = c_dist + weight[l]
                    elif _to[line] != n_link:
                        n_dist = c_dist + weight[l]
                    else:
                        n_dist = c_dist + weight[l] + delay[line]
                        line += 1
                except:  # todo 这里不太好，最好还是把turn_table 的最后一行变成NULL
                    n_dist = c_dist + weight[l]

                if n_dist < dist[l]:
                    arc_pred[l] = c_line
                    dist[l] = n_dist
                    costs_heap.push_if_lower(n_dist, l)
        else:  # When no turning delay
            for l in range(start_l, end_l):
                n_dist = c_dist + weight[l]

                if n_dist < dist[l]:
                    arc_pred[l] = c_line
                    dist[l] = n_dist
                    costs_heap.push_if_lower(n_dist, l)

