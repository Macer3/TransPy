# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np
import re
from itertools import product
import transpy as tp

ID_TYPE = tp.ID_TYPE
NULL = tp.NONE


def get_field_dict(fields):
    """
    将 `StreetTable` 中的域名转换为 `Net` 中对应的域名.

    `StreetTable` 中, 道路两个方向的属性存在同一行中, 以 ``AB`` 开头的域表示道路
    正向的属性, 以 ``BA`` 开头则表示道路反向的属性, 不区分大小写.

    `Net` 中的每行只储存道路一个方向的属性, 故将 `StreetTable` 中的域名转换为
    `Net` 中的域时, 需除掉 `StreetTable` 中表示方向的前缀.

    Parameters
    ----------
    fields : list
        由域名组成的列表.

    Returns
    -------
    fields_dict : dict
        字典的键为 `Net` 中的域名, 值为一2个元素的列表, 列表的第1个元素表示原域名
        中的正向域名, 第2个元素表示原域名中的反向域名. 若原域名不具有方向性, 则两个
        元素都和域名相同.

    Examples
    --------
    >>> fields = ['LENGTH', 'DIR', 'capacity', 'AB_speed', 'BA_speed',
    ...          'ab_times', 'ba_times', 'Ba_v/c', 'Ab_v/c']
    >>> get_field_dict(fields)
    {'DIR': ['DIR', 'DIR'],
    'LENGTH': ['LENGTH', 'LENGTH'],
    'capacity': ['capacity', 'capacity'],
    'speed': ['AB_speed', 'BA_speed'],
    'times': ['ab_times', 'ba_times'],
    'v/c': ['Ab_v/c', 'Ba_v/c']}

    """
    ab = re.compile('^[A|a][B|b]_?(.*)')
    ba = re.compile('^[B|b][A|a]_?(.*)')
    ab_list = []
    ba_list = []

    def _match(regex, word):
        result = regex.search(word)
        if result:
            return result.groups()[0]

    for mem in fields:
        ab_list.append(_match(ab, mem))
        ba_list.append(_match(ba, mem))
    fields_dict = {}
    for i, mem in enumerate(fields):
        ab_mem = ab_list[i]
        ba_mem = ba_list[i]
        if ab_mem is None and ba_mem is None:
            fields_dict[mem] = [mem, mem]
        elif ab_mem is None:
            try:
                idx = ab_list.index(ba_mem)
                fields_dict[ba_mem] = [fields[idx], mem]
            except ValueError:
                fields_dict[mem] = [mem, mem]
        else:  # ba_mem is None and ab_mem is not None
            try:
                idx = ba_list.index(ab_mem)
                fields_dict[ab_mem] = [mem, fields[idx]]
            except ValueError:
                fields_dict[mem] = [mem, mem]

    return fields_dict


def get_net_len(dir_field):
    """
    确定 `Net` 的总行数.

    Parameters
    ----------
    dir_field : ndarray
        `StreetTable` 中表示道路方向的那一列, ``StreetTable['DIR']``.

    Returns
    -------
    int : `net` 的行数.
    """
    n = 2 * len(dir_field)
    for i in dir_field:
        if i != 0:
            n -= 1
    return n


# noinspection PyUnboundLocalVariable
def get_idx(column):
    """计算索引数组.

    Parameters
    ----------
    column : ndarray
        需索引的那一列, 应事先从小到大排序过.

    Returns
    -------
    idx : ndarray
        索引数组.
    """
    column_len = len(column)
    idx = np.full((column[-1] + 1,), NULL, np.uint16)
    last_id = column[0]  # todo net 里应该有个最小的ID标记，不然不知道是否无效
    idx[last_id - 1] = 0
    for i in range(column_len):
        now_id = column[i]
        if now_id != last_id:
            idx[now_id - 1] = i
            idx[last_id] = i
            last_id = now_id
    idx[now_id] = i + 1
    return idx


def get_trace(idx, data_part, r_data_part):
    """计算正向与反向星型表示法中的对应关系的数组.

    Parameters
    ----------
    idx : ndarray
        正向索引数组.
    data_part : structured array
        正向的 `Net` 数据, 应包括 `ID`,`START_NODE`,`END_NODE` 三个域.
    r_data_part : structured array
        反向 `Net` 数据, 应包括 `ID`,`START_NODE`,`END_NODE` 三个域.

    Returns
    -------
    trace : ndarray
        正向与反向星型表示法中的对应关系的数组.
    """
    column_len = data_part.shape[0]
    dtype = np.min_scalar_type(column_len)
    trace = np.empty(column_len, dtype)
    for i in range(column_len):
        start_node = r_data_part[i]['START_NODE']
        end_node = r_data_part[i]['END_NODE']
        ID = r_data_part[i]['ID']
        for j in range(idx[start_node - 1], idx[start_node]):
            if data_part[j]['END_NODE'] == end_node and \
                            data_part[j]['ID'] == ID:
                trace[i] = j
                break
    return trace


def get_net_data(street_data, fields):
    """将存储道路信息的表进行转换. 得到 `Net` 所需的数据.

    Parameters
    ----------
    street_data : structured array
        存储道路信息的 `structured array`.
    fields : list[str]
        A list of fields which need to be included in `Net`, apart from
        ['ID', 'START_NODE', 'END_NODE','DIR'].

    Returns
    -------
    data : ndarray
        `Net` 中数据的主体部分.
    idx : ndarray
        `Net` 的正向索引.
    r_idx : ndarray
        `Net` 的反向索引.
    trace : ndarray
        表示 `Net` 中的各行在正向与反向星型表示法中的对应关系的数组.
    """
    # 确定net中dtype的names
    builtin_fields = ['START_NODE', 'END_NODE', 'ID']
    names = street_data.dtype.names
    for name in builtin_fields:
        if name not in names:
            raise ValueError("No \"{}\" in street_data's field".format(name))
        if name in fields:
            fields.remove(name)
    if 'DIR' not in names:
        raise ValueError("No \"DIR\" in street_data's field")
    fields_dict = get_field_dict(fields)
    names = builtin_fields + list(fields_dict) + ['FLAG']

    # 确定net中dtype的formats
    for key, value in fields_dict.items():
        if street_data[value[0]].dtype != street_data[value[1]].dtype:
            raise TypeError("{0} and {1} has different dtype".
                            format(value[0], value[1]))
    formats = [ID_TYPE, ID_TYPE, ID_TYPE] + \
              [street_data[a[0]].dtype for a in fields_dict.values()] + \
              ['u1']

    # 初始化net
    num = get_net_len(street_data['DIR'])
    data = np.zeros((num,), dtype=({'names': names, 'formats': formats}))

    # fill net with street_data
    def fill(data, d_i, street_data, s_i, fields_dict):
        data[d_i]['START_NODE'] = street_data[s_i]['START_NODE']
        data[d_i]['END_NODE'] = street_data[s_i]['END_NODE']
        data[d_i]['ID'] = street_data[s_i]['ID']
        for key, value in fields_dict.items():
            data[d_i][key] = street_data[s_i][value[0]]

    def fill_reverse(data, d_i, street_data, s_i, fields_dict):
        data[d_i]['START_NODE'] = street_data[s_i]['END_NODE']
        data[d_i]['END_NODE'] = street_data[s_i]['START_NODE']
        data[d_i]['ID'] = street_data[s_i]['ID']
        for key, value in fields_dict.items():
            data[d_i][key] = street_data[s_i][value[1]]

    d_i = 0  # d_i: data's idx, s_i: street_data's idx
    for s_i in range(len(street_data)):
        if street_data[s_i]['DIR'] == 0:
            fill(data, d_i, street_data, s_i, fields_dict)
            d_i += 1
            fill_reverse(data, d_i, street_data, s_i, fields_dict)
        elif street_data[s_i]['DIR'] > 0:
            fill(data, d_i, street_data, s_i, fields_dict)
        else:
            fill_reverse(data, d_i, street_data, s_i, fields_dict)
        d_i += 1

    # Sort data, get idx, r_idx and trace
    data = np.sort(data, order=['START_NODE', 'ID', 'END_NODE'])
    r_data_part = np.sort(data[['START_NODE', 'END_NODE', 'ID']],
                          order=['END_NODE', 'ID', 'START_NODE'])
    idx = get_idx(data['START_NODE'])
    r_idx = get_idx(r_data_part['END_NODE'])
    trace = get_trace(idx, data[['START_NODE', 'END_NODE', 'ID']],
                      r_data_part)

    return data, idx, r_idx, trace


def update_net_flag(net, turn_table):
    """
    更新 `net` 中的转向延误标志列.

    Parameters
    ----------
    net : Net
    turning_table : IDGroupTable
        转向表
    
    Notes
    -----
    如果对于某顶点, `turn_table` 中的转向与 `net` 中的边不对应, 那么直接忽略
    该转向, 不会抛出提示或错误.
    """
    if not turn_table.sorted():
        turn_table.sort_and_idx()
    from_street = 0
    turning_data = turn_table._data
    turning_idx = turn_table.idx
    net_data = net._data
    r_idx = net.r_idx
    trace = net.trace
    for i in range(len(turn_table)):
        turning_rec = turning_data[i]
        foo = turning_rec['FROM']
        if from_street == foo:
            continue
        from_street = foo
        node = turning_rec['ID']
        line1 = r_idx[node - 1]  # todo 这里加个错误检查机制，万一net中没有响应的node呢
        line2 = r_idx[node]
        target_lines = trace[line1:line2]
        aim_ids = net_data['ID'][target_lines]
        target_line = target_lines[aim_ids == from_street][0]
        flag = turning_idx[node] - i
        net_data[target_line]['FLAG'] = flag


def net_to_turn_table(net, node_id=None, names=None, formats=None,
                      base_table=None, exclude=True, node_table=None):
    """对 `net` 中的各交叉口生成转向表.

    对 `net` 中指定的 `node_ID` 生成转向表, 可设定新转向表的域, 如果同时
    提供了一个旧表 `base_table`, 新生成的转向表会拷贝旧表中对应的数据.

    Parameters
    ----------
    net : net
    node_id : array_like, optional
        需要生成转向表的交叉口的 `ID` 号, Default: 对所有交叉口生成转向表.
    names : list[str], optional
        每一个转向表必有 `ID`, `FROM`, `TO`, `DELAY` 这4个域, 如果想要所生成的
        转向表包含其他域, 可在 `names` 中指定域的名称.
        Default: ``names = ['volume']``.
    formats : list[str], optional
        `format` 为 `names` 中各个域对应的格式, 长度需和 `names` 相同.
    base_table : IDGroupTable, optional
        一个现有的转向表, 如果有的话, 可将其中相对应的数据复制到新生成的转向表中.
    exclude : bool, optional
        是否排除形心点(产生与吸引点). 若要排除产生于吸引点, 需提供 `node_table`,
        根据 `node_table` 中的 `type` 域判断该节点是否为形心点. Default: True.
    node_table : IDTable, optional
        根据 `node_table` 中的 `type` 域判断是否是形心点, 标号为255的视为形心.

    Returns
    -------
    turn_table : IDGroupTable
        基于 `net` 生成的转向表, 按 ``['ID','FROM','TO']`` 升序排列过.
    """
    if exclude:
        if node_table is None:
            print('No node_table, so the output turning_table may '
                  'contain centroid.')
            exclude = False
        elif 'type' not in node_table.fields:
            print("No 'type' fields in node_table, so the output "
                  "turning_table may contain centroid.")
            exclude = False

    # Get names, formats and copy_field_name(if have).
    if names is None:
        names = ['volume']
        if formats is None:
            formats = ['f8']
    num = len(names)
    if num != len(formats):
        raise ValueError('Length of names and formats not same.')
    if len(set(names)) != num:
        raise ValueError('names not unique')
    builtin_names = ['ID', 'FROM', 'TO', 'DELAY']
    foo = []
    for name in builtin_names:
        if name in names:
            foo.append(names.index(name))
    for i in foo:
        names.__delitem__(i)
        formats.__delitem__(i)
    copy_fields = set()
    if base_table:
        base_table.sort_idx()
        copy_fields = set(names).intersection(base_table.names)
    names = builtin_names + names
    formats = [ID_TYPE, ID_TYPE, ID_TYPE, 'f8'] + formats

    def get_node_link(data, field, node_id):
        """
        找到以节点为起/终点的道路信息.

        Parameters
        ----------
        data : structured array
            就是 `net._data`.
        field : {'START_NODE', 'END_NODE'}
            为 `'START_NODE'` 时统计以给定节点为起点的道路信息,
            为 `'START_NODE'` 时统计以给定节点为终点的道路信息.
        node_id : set
            A set of nodes's ID which need to be counted.

        Returns
        -------
        dict :
            返回字典的键为 `node` 的 `ID`, 值为以 `node` 为起点/终点的所有
            道路的 `ID` 组成的列表.
        """
        link_dict = {i: [] for i in node_id}
        for line in data:
            ID = line[field]
            if ID in node_id:
                link_dict[ID].append(line['ID'])
        return link_dict

    # Get the `nodes`, which is a set of target nodes.
    nodes = set(net._data['START_NODE'])
    nodes.intersection_update(set(net._data['END_NODE']))
    if node_id is not None:
        node_id = set(node_id)
        nodes.intersection_update(node_id)
        if len(nodes) < node_id:
            print('Some node_IDs not in net, have removed them.')
    start_dict = get_node_link(net._data, 'START_NODE', nodes)
    end_dict = get_node_link(net._data, 'END_NODE', nodes)

    # Determine the number of lines of the turning_table.
    line_num = 0
    for node in nodes:
        if exclude:
            line_num = node_table.ID_map[node]
            foo = node_table._data[line_num]['type']
            if foo != 255:
                line_num += len(start_dict[node]) * len(end_dict[node])
                continue
        line_num += len(start_dict[node]) * len(end_dict[node])

    turning_table = np.zeros((line_num,), dtype={'names': names,
                                                 'formats': formats})
    # Now begin to fill in the table.
    i = 0
    for node in nodes:
        pro = product(end_dict[node], start_dict[node])
        for mem in pro:
            turning_table[i]['ID'] = node
            turning_table[i]['FROM'] = mem[0]
            turning_table[i]['TO'] = mem[1]
            if copy_fields:
                copy_line = base_table.get_line_num(node, mem[0], mem[1])
                for name in copy_fields:
                    turning_table[i][name] = base_table[copy_line][name]
            i += 1

    turning_table.sort(order=['ID', 'FROM', 'TO'])
    return turning_table
