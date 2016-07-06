# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np
import transpy as tp
from transpy.compute.core import c_all_or_nothing
from transpy.compute.shortest_way import get_sp_param

NONE = tp.NONE
INF = np.inf
ID_TYPE = tp.ID_TYPE


class AssignConfig:
    """用于配置交通分配参数设置的类.

    Attributes
    ----------
    method : str
        Currently 'AON' or 'UE'.
    time_field : str
        The field to access time from data.
    capacity_field : str
        The field to access capacity from data.
    turn_delay_type : {'none','ban','all'}, optional
        计算转向延误的方式, 为 'none' 时不计算转向延误, 'ban' 时仅考虑禁止转
        向, 为 'all' 时计算转向表中的所有转向. Default: 'all'.
    preload_field : str
        The field to access preload flow from data.
    focus_nodes : array_like or str, optional
        Default: `None`, 'all' for all nodes.
    alpha_field : str
        The field to access varBox alpha from data.
    beta_field : str
        The field to access varBox beta from data.
    global_alpha : float
    global_beta : float
    convergence : float
    max_iteration : int
    arc_type_field : str
    arc_type_dict : dict
    """

    def __init__(self):
        self.method = 'AON'
        self.time_field = None
        self.capacity_field = None
        self.turn_delay_type = 'all'
        self.preload_field = None
        self.focus_nodes = None
        self.alpha_field = 'alpha'
        self.beta_field = 'beta'
        self.global_alpha = 0.15
        self.global_beta = 4
        self.convergence = 0.001
        self.max_iteration = 20
        self.arc_type_field = None
        self.arc_type_dict = None
        self.print_frequency = 1


class AssignSummary:
    """ 用于记录交通分配迭代过程参数变化的类.

    Attributes
    ----------
    step : list
        A list to record `step` in every iteration.
    max_flow_change : list
        A list to record `max_flow_change` in every iteration.
    relative_gap : list
        A list to record `relative-gap` in every iteration.
    equilibrium_reached : bool
        When assignment reached convergence, it's `True`, else `False`.
    """
    __slots__ = ('step','max_flow_change','relative_gap',
                 'equilibrium_reached')

    def __init__(self):
        self.step = []
        self.max_flow_change = []
        self.relative_gap = []
        self.equilibrium_reached = False


class Counter:
    """用于控制迭代过程中打印频率的计数器."""
    def __init__(self,num):
        self.num = num
        self.current_num = 0

    def add(self):
        if self.num == 0:
            return False
        self.current_num += 1
        if self.current_num == self.num:
            self.current_num =0
            return True


def all_or_nothing(net, matrix, link_table, cfg):
    """全有全无分配.

    Parameters
    ----------
    net : Net
    matrix : Matrix
    link_table : IDTable
    cfg : AssignConfig

    Returns
    -------
    flow_data : structured array
        一个记录着分配结果的结构数组，它包括 `ID`, `AB_FLOW`, `BA_FLOW` 这几个域.
    turn_data : structured array
        一个记录着交叉口转向流量的结构数组，它包括 `ID`, `FROM`, `TO`, `FLOW` 这
        几个域. 只有在 `cfg.focus_node` 中指明的交叉口才记录转向.

    See Also
    --------
    user_equilibrium
    """

    data = net._data
    time = get_assign_param(data, cfg.time_field, cfg.arc_type_field,
                            cfg.arc_type_dict)
    flag, turn_idx, from_link, to_link, delay, dist, node_pred, arc_pred = \
        get_sp_param(net, cfg.turn_delay_type)
    a, b, turns_flow = prepare_focus_nodes(net, cfg.focus_nodes)
    arcs_flow = np.zeros(data.shape, np.float64)

    c_all_or_nothing(matrix._row_idx, matrix._col_idx, matrix._data,
                     net.idx, data['ID'], data['END_NODE'], time,
                     flag, turn_idx, from_link, to_link, delay, dist,
                     node_pred, arc_pred, arcs_flow, a, b, turns_flow)

    flow_data = net_to_link_flow(link_table, net, arcs_flow)
    turn_data = _get_turn_data_from_runtime(net, a, b, turns_flow)

    return flow_data, turn_data


def user_equilibrium(net, matrix, link_table, cfg):
    """全有全无分配.

    Parameters
    ----------
    net : Net
    matrix : Matrix
    link_table : IDTable
    cfg : AssignConfig

    Returns
    -------
    flow_data : structured array
        一个记录着分配结果的结构数组，它包括 `ID`, `AB_FLOW`, `BA_FLOW` 这几个域.
    turn_data : structured array
        一个记录着交叉口转向流量的结构数组，它包括 `ID`, `FROM`, `TO`, `FLOW` 这
        几个域. 只有在 `cfg.focus_node` 中指明的交叉口才记录转向.
    summary : AssignSummary
        记录着分配迭代过程的结构.

    See Also
    --------
    all_or_nothing
    """
    # Basic setup
    summary = AssignSummary()
    data = net._data
    type_field = cfg.arc_type_field
    type_dict = cfg.arc_type_dict
    time0 = get_assign_param(data, cfg.time_field, type_field, type_dict)
    time = time0.copy()
    flag, turn_idx, from_link, to_link, delay, dist, node_pred, arc_pred = \
        get_sp_param(net, cfg.turn_delay_type)
    counter = Counter(cfg.print_frequency)

    # Setup about BPR function parameters
    capacity = get_assign_param(data, cfg.capacity_field, type_field,
                                type_dict)
    alpha = get_assign_param(data, cfg.alpha_field, type_field, type_dict,
                             cfg.global_alpha)
    beta = get_assign_param(data, cfg.beta_field, type_field, type_dict,
                            cfg.global_beta)

    # Setup about focus node
    a, b, turns_flow1 = prepare_focus_nodes(net, cfg.focus_nodes)
    turns_flow2 = turns_flow1.copy()
    if a.shape[0] == 1:
        turns_diff = None
    else:
        turns_diff = turns_flow1.copy()

    # Setup about preload
    if cfg.preload_field:
        preload_flow = get_assign_param(data, cfg.preload_field, type_field,
                                        type_dict)
        # Update time before first assignment
        bpr_fun(time0, alpha, beta, capacity, time, preload_flow)
    else:
        preload_flow = None

    arcs_flow1 = np.zeros(data.shape, np.float64)
    arcs_flow2 = arcs_flow1.copy()
    diff = arcs_flow1.copy()
    f = lambda x: derivative(x, arcs_flow1, diff, time0, alpha, beta,
                             capacity, preload_flow)
    c_all_or_nothing(matrix._row_idx, matrix._col_idx, matrix._data,
                     net.idx, data['ID'], data['END_NODE'], time,
                     flag, turn_idx, from_link, to_link, delay, dist,
                     node_pred, arc_pred, arcs_flow1, a, b, turns_flow1)

    # Main loop
    for i in range(1, cfg.max_iteration):
        # Update road time
        bpr_fun(time0, alpha, beta, capacity, time, arcs_flow1, preload_flow)

        c_all_or_nothing(matrix._row_idx, matrix._col_idx, matrix._data,
                         net.idx, data['ID'], data['END_NODE'], time,
                         flag, turn_idx, from_link, to_link, delay, dist,
                         node_pred, arc_pred, arcs_flow2, a, b, turns_flow2)

        # Find the best update step.
        np.subtract(arcs_flow2, arcs_flow1, diff)
        step = double_secant10(0, 1, f)
        summary.step.append(step)
        # Update arcs flow.
        diff *= step
        arcs_flow1 += diff

        # Update turns flow.
        if turns_diff is not None:
            np.subtract(turns_flow2, turns_flow1, turns_diff)
            turns_diff *= step
            turns_flow1 += turns_diff

        # Max Flow Change
        diff = np.abs(diff, diff)
        max_flow_change = diff.max()
        summary.max_flow_change.append(max_flow_change)
        # Relative Gap
        relative_gap = 1 - np.sum(time * arcs_flow2) / np.sum(time * arcs_flow1)
        summary.relative_gap.append(relative_gap)

        # whether print to screen
        if counter.add():
            print('Iter{}: step={}, relative_gap={}, max_flow_change={}'.
                  format(i, step, relative_gap, max_flow_change))

        # Check convergence
        if relative_gap <= cfg.convergence:
            break
        arcs_flow2.fill(0)
        turns_flow2.fill(0)

    flow_data = net_to_link_flow(link_table, net, arcs_flow1)
    turn_data = _get_turn_data_from_runtime(net, a, b, turns_flow1)

    return flow_data, turn_data, summary


def bpr_fun(time0, alpha, beta, capacity, time1, arcs_flow,
            preload_flow=None):
    """BPR函数.

    time1 = time0 * (1 + alpha * (arcs_flow / capacity) ** beta)
    """
    np.copyto(time1, arcs_flow)
    if preload_flow is not None:
        time1 += preload_flow
    time1 /= capacity
    time1 **= beta
    time1 *= alpha
    time1 += 1
    time1 *= time0


def derivative(step, arcs_flow1, diff, time0, alpha, beta, capacity,
               preload_flow):
    """The derivative which need to be zeros in iteration.

    np.sum((diff * time0 * (1 + alpha *
        ((preload_flow + arcs_flow1 + step * diff) /
         capacity) ** beta))
    """
    foo = diff.copy()
    foo *= step
    foo += arcs_flow1
    if preload_flow is not None:
        foo += preload_flow
    foo /= capacity
    foo **= beta
    foo *= alpha
    foo += 1
    foo *= time0
    foo *= diff
    return foo.sum()


def double_secant10(x0, x1, f, error=0.1, max_iter=100):
    """改进后的两点弦截法.

    Using double_secant10 method to find a root of f.

    Parameters
    ----------
    x0, x1: int/float
        搜索区间边界.
    f : function
        求根函数， 需要是连续的。
    error : float, optional
        允许误差, Default: 0.1.
    max_iter : int, optional
        最大迭代次数, Default: 50.

    Returns
    -------
    float: root of f.

    Notes
    -----
    ``f(x0)`` and ``f(x1)`` should have opposite signs,
    else either `x0` or `x1` will be return according to
    ``f(x0), f(x1)`` which is closer to 0.
    """
    y0 = f(x0)
    y1 = f(x1)
    # Algorithm assumes f(x0)<0 and f(x1)>0,
    # if f(x0)>0 and f(x1)<0, then switch x0 and x1.
    if y0 <= 0:
        if y1 <= 0:
            #  f(x0) and f(x1) both <= 0
            if y0 < y1:
                return x1
            else:
                return x0
    else:
        if y1 <= 0:
            y3 = y0
            y0 = y1
            y1 = y3
            x3 = x0
            x0 = x1
            x1 = x3
        else:
            #  f(x0) and f(x1) both > 0
            if y0 < y1:
                return x0
            else:
                return x1

    # Main loop
    for i in range(max_iter):
        if y1 / y0 < -10:
            x3 = 0.9 * x0 + 0.1 * x1
        else:
            x3 = -y0 * (x1 - x0) / (y1 - y0) + x0
        y3 = f(x3)
        if abs(y3) <= error:
            return x3
        if y3 < 0:
            x0 = x3
            y0 = y3
        else:
            x1 = x3
            y1 = y3

    Warning('Max iter number {} reached, double secant stop with error {}'.
          format(max_iter, y3))
    return x3


def get_assign_param(data, field, type_field=None,
                     type_dict=None, global_value=None):
    """Prepare and validate parameters for network assignment.

    Parameters in traffic assignment (time, capacity, alpha and beta) should
    be non-negative, value less than zero or nan will be consider as invalid
    value.

    Parameters
    ----------
    data : structured array
    field : str
        The field or key to access parameter from `data` or `type_dict`.
        If simply use a global value, `field` is just a name string.
    type_field : str
        A field of the data in which stores the arcs's type information.
    type_dict : dict
        A type-information dictionary.
    global_value : float
        The global value of this parameter.

    Returns
    -------
    ndarray / float :
        Try to return a view of data (``data[field]``). If there exists
        invalid value or no such `field` in `data`, return a new ndarray
        which fill the invalid value with the value defined in `type_dict`
        and global value.
        If only the global value are available, return the global value.

    Raises
    ------
    ValueError :
        If can't make all the value valid.
    """
    param = None
    shape = data.shape
    field_is_right = False  # Prevent a wrong field

    # Try to get varBox from data
    if field in data.dtype.fields:
        field_is_right = True
        param = np.array(data[field], dtype='f8', copy=False)
        invalid = ~(param >= 0)
        # If values are all valid, then return
        if invalid.nonzero()[0].shape[0] == 0:
            return param
        else:
            # Copy it, no change to original varBox
            param = param.copy()

    # Try to fill invalid value with the predefined value in type_dict
    if type_field is not None and type_dict is not None:
        type_param = data[type_field]
        if param is None:
            param = np.full(shape, -1, dtype='f8')
            invalid = np.full(shape, True, dtype='bool')
        for arc_type, arc_dict in type_dict:
            default_val = arc_dict.get(field)
            if default_val:
                field_is_right = True
                param[invalid & (type_param == arc_type)] = default_val
        invalid = ~(param >= 0)
        # If values are all valid, then return.
        if invalid.nonzero()[0].shape[0] == 0:
            return param

    # If still has invalid value, fill with global value.
    if global_value:
        try:
            if not global_value > 0:
                raise ValueError('global_value {} of "{}" '
                                 'is invalid'.format(global_value, field))
        except TypeError:
            raise TypeError('Wrong global_value type of "{}".'.format(field))

        if param is None:
            param = global_value
        else:
            param[invalid] = global_value
        return param

    # Check if all value are valid, or raise an error.
    if field_is_right is False:
        Warning('no field or key "{}".'.format(field))
    if param is None:
        raise ValueError('No valid value assign to varBox "{}".'.format(field))
    lines = invalid.nonzero()[0]
    if lines.shape[0] == 0:
        return param
    else:
        raise ValueError("Invalid value(s) {} in {}, line(s) {}···.".
                         format(param[lines[0]], field, lines[0]))


def net_to_link_flow(link_table, net, arcs_flow):
    """将与网络文件对应的弧流量转换为路段流量.

    Parameters
    ----------
    link_table : IDTable
    net : Net
    arcs_flow : ndarray

    Returns
    -------
    link_flow : structured array
        A structured array which contains fields of `ID`, `AB_FLOW`
        and `BA_FLOW`.
    """
    mapping = net_to_table_mapping(net, link_table)
    link_flow = np.empty(len(link_table),
                      dtype={'names': ['ID', 'AB_FLOW', 'BA_FLOW'],
                             'formats': [ID_TYPE, 'f8', 'f8']})
    link_flow['ID'] = link_table['ID']
    link_flow['AB_FLOW'] = arcs_flow[mapping['AB']]
    link_flow['AB_FLOW'][link_table['DIR'] < 0] = np.nan
    link_flow['BA_FLOW'] = arcs_flow[mapping['BA']]
    link_flow['BA_FLOW'][link_table['DIR'] > 0] = np.nan
    return link_flow

def prepare_focus_nodes(net, focus_nodes):
    """为需要记录转向的交叉口准备相关数据."""
    data = net._data
    if focus_nodes is None or len(focus_nodes) == 0:
        a = np.full((1, ), NONE, ID_TYPE)
        b = a
        turns_flow = np.zeros((1, ), 'f8')
        return a, b, turns_flow
    else:
        if focus_nodes == 'all':
            focus_nodes = np.unique(data['START_NODE'])
        else:
            focus_nodes = np.array(focus_nodes, ID_TYPE, copy=False)
        a = np.full(data.shape, NONE, ID_TYPE)
        b = a.copy()
        lines = _runtime_turn_idx(net, focus_nodes, a, b)
        turns_flow = np.zeros((lines,), np.float64)
        return a, b, turns_flow


def _runtime_turn_idx(net, nodes, a, b):
    """Get the runtime index array to fast fill turns_flow.

    Parameters
    ----------
    net : Net
    a, b : ndarray
         Runtime index array to fast fill turns_flow. In here the initial
         input value should be all NONEs.

    Returns
    -------
    total_line : ID_TYPE
    """
    idx = net.idx
    r_idx = net.r_idx
    trace = net.trace
    a_line = 0
    total_line = 0
    for i in range(nodes.shape[0]):
        node = nodes[i]

        start_a = r_idx[node - 1]
        if start_a == NONE:
            continue
        end_a = r_idx[node]
        if end_a == NONE:
            continue
        start_b = idx[node - 1]
        if start_b == NONE:
            continue
        end_b = idx[node]
        if end_b == NONE:
            continue

        in_arc_num = end_a - start_a
        out_arc_num = end_b - start_b
        turn_nums = out_arc_num * in_arc_num
        if turn_nums <= 3:  # Only count node with more than three turns
            continue
        total_line += turn_nums

        for line in range(start_a, end_a):
            arc = trace[line]
            a[arc] = a_line
            a_line += out_arc_num
        b_line = 0
        for arc in range(start_b, end_b):
            b[arc] = b_line
            b_line += 1

    return total_line


def net_to_table_mapping(net, link_table):
    """Get an mapping array to map net data to link data.

    Parameters
    ----------
    net : Net
        The corresponding net of the link table.
    link_table : IDTable
        The corresponding link table and `net`.

    Returns
    -------
    mapping :
    A structured array with field `AB` and `BA`.
    """
    net_id = net._data['ID']
    net_start = net._data['START_NODE']
    mapping = np.empty(len(link_table), dtype={'names': ['AB', 'BA'],
                                               'formats': [ID_TYPE, ID_TYPE]})
    ID_map = link_table.ID_map
    link_start = link_table['START_NODE']
    _dir = link_table['DIR']
    for i in range(len(net)):
        line = ID_map[net_id[i]]
        if _dir[line] == 0:
            if net_start[i] == link_start[line]:
                mapping[line]['AB'] = i
            else:
                mapping[line]['BA'] = i
        else:
            mapping[line]['AB'] = i
            mapping[line]['BA'] = i
    return mapping


def _get_turn_data_from_runtime(net, a, b, turns_flow):
    """Get turn data from_runtime.

    Parameters
    ----------
    net :
    a :
    b :
    turns_flow :

    Returns
    -------
    turn_data : structured array
        一个记录着交叉口转向流量的结构数组，它包括 `ID`, `FROM`, `TO`, `FLOW` 这
        几个域.
    """
    data = net._data
    _id = data['ID']
    end_node = data['END_NODE']
    idx = net.idx
    turn_data = np.zeros(turns_flow.shape,
                         dtype={'names': ['ID', 'FROM', 'TO', 'FLOW'],
                                'formats': [ID_TYPE, ID_TYPE, ID_TYPE,
                                            np.float64]})
    turn_data['FLOW'] = turns_flow
    for from_arc in range(a.shape[0]):
        from_stride = a[from_arc]
        if from_stride != NONE:
            from_link = _id[from_arc]
            node_id = end_node[from_arc]
            start_b = idx[node_id - 1]
            end_b = idx[node_id]
            for to_arc in range(start_b, end_b):
                to_stride = b[to_arc]
                now_line = from_stride + to_stride
                turn_data[now_line]['ID'] = node_id
                turn_data[now_line]['FROM'] = from_link
                turn_data[now_line]['TO'] = _id[to_arc]

    return turn_data
