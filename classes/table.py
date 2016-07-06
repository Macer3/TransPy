# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np
from heapq import heappop, heappush, heapify
from collections import Iterable
from transpy.classes.convert import get_idx
from transpy.classes.tool import check_positive, check_int

# noinspection PyAttributeOutsideInit
class Table(object):
    """各种Table的基类.

    `Table` 中的主要数据部分为一个 `structured array`. 与 `structured array`
    不同的是, 增删 `Table` 的行时, 不会每次都重新分配一个新表, 数据在编辑时
    留有空行, 所以往 `Table` 中增删元素时效率较高.

    Parameters
    ----------
    data : structured array
        表中的主要数据部分, `data` 中必须存在名称为 `ID` 的域, 否则无法初始化.

    Attributes
    ----------
    names : tuple
    dtype : numpy.dtype

    See Also
    --------
    IDGroupTable
    IDTable

    Notes
    -----
    * `data` 中必须存在名称为 `ID` 的域, 而且有效的 `ID` 必须是正整数. 程序内
      部通过 `ID` 判断一行是否有效, 若 ``ID <= 0``, 那么该行会被视为空白行, 调
      用 `pack` 方法时将会清除掉所有空白行.
    * `Table` 内部的 `_line_heap` 储存着表中空行的位置, 它是一个优先列队, 每次
      调用 `next_line_num` 方法的时候, 将返回下一个空白行中最小的行号.

    .. warning:: 尽管可以直接修改每行记录的 `ID`, 但强烈建议不要这么做, 即使您
       很清楚程序内部的工作机制. 程序内部通过一系列手段来记录当前表中的空白行
       号, `ID` 号, 以及行号与 `ID` 之间的对应关系, 直接修改 `ID` 容易造成系统
       内部混乱, 甚至造成有效的数据行被删除. 一般情况下无需修改 `ID`, 如需修改
        `ID` 请使用类内自带方法.
    """
    def __init__(self, data): # todo 允许data为None
        if not isinstance(data, np.ndarray):
            raise TypeError('Data must be a np.ndarray ')
        if 'ID' not in data.dtype.fields:
            raise ValueError('No "ID" in fields')

        self._data = data
        self._view_line_order = np.arange(data.shape[0])
        self._view_name_order = list(data.dtype.names)
        self.changed = True
        self._line_heap = []
        self.modify_mode = False

    def set_fields(self):
        pass

    def sort_view(self, field, order=1):
        if order not in [1, -1]:
            raise ValueError('order should be 1 or -1')
        idx = np.argsort(self._data, order=field)
        if order == 1:
            self._view_line_order = idx
        else:
            self._view_line_order = idx[::-1]

    def __len__(self):
        return self._data.shape[0]

    @property
    def names(self):
        """返回表中数据各列的域名."""
        return self._data.dtype.names


    @property
    def dtype(self):
        """表中数据各列的数据类型信息."""
        return self._data.dtype

    @property
    def shape(self):
        """表中数据各列的域名及其数据类型组成的字典."""
        return self._data.shape

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def next_line_num(self, update=False):
        """返回现空白行中最小的那一行的行号.

        Parameters
        ----------
        update : bool, optional
            是否更新内部计数数据, 为 `True` 时更新, 为 `False` 时不更新. 如更
            新数据, 连续两次调用该函数的返回值不同, 如不更新数据, 连续两次调用
            该函数的返回值相同. Defualt : `False`.
        
        Returns
        -------
        int : 现空白行中最小的那一行的行号.
        """
        try:
            while self._data[self._line_heap[0]]['ID'] != 0:
                heappop(self._line_heap)
            if update:
                num = heappop(self._line_heap)
            else:
                num = self._line_heap[0]
        except IndexError:
            num = len(self._data)
        return num

    def del_line(self, num):
        """清空表中的行, 可以同时清空多行.

        Parameters
        ----------
        num : int, Iterable[int]
            所要清空的行对应行号(或行号列表).
        """
        if isinstance(num, Iterable):
            for n in num:
                self._del_a_line(n)
        else:
            self._del_a_line(num)


    def _del_a_line(self, line_num):
        """清空表中的一行."""
        check_int(line_num)
        self._data[line_num] = np.zeros((1,), self._data.dtype)
        heappush(self._line_heap, line_num)

    def find_effect_line(self):
        """返回所有有效的行的序号.

        Returns
        -------
        ndarray : 有效行的行号.
        """
        return np.where((self._data['ID'] > 0))[0]


    def pack(self):
        """删除table中的所有空白行.

        Notes
        -----
        程序内部通过 `ID` 判断一行是否有效, 所有 ``ID <= 0`` 的行会被视为空白
        行, 调用 `pack` 方法将被清除掉.
        """
        effect_line = self.find_effect_line()
        if len(effect_line) == len(self._data):
            return
        else:
            self._data = np.array(self._data[effect_line])
            self._line_heap = []
            self.changed = True

    def expand(self, lines=50):
        """增加在table的行数.

        在 `table` 后面增加 `lines` 行空白行.

        Parameters
        ----------
        lines : int
            要增加的行数.
        """
        now_line = len(self._data)
        foo = np.zeros((lines,), dtype=self._data.dtype)
        self._data = np.hstack((self._data, foo))
        # update line_heap
        self._line_heap.extend(range(now_line, now_line + lines))
        heapify(self._line_heap)


class IDTable(Table):
    """一种用来储存道路, 交叉口信息的数据结构.

    `IDTable` 各行间 `ID` 不能重复. 每个 `ID` 对应一条道路或者一个交叉口.

    Parameters
    ----------
    data : structured array
        表中的主要数据部分, `data` 中必须存在名称为 `ID` 的域, 否则无法初始化.

    Attributes
    ----------
    names
    fields
    ID_map : dict
        一个字典, 键为 `ID`, 值为该 `ID` 所对应的行号.
    now_max_ID : int
        当前最大 `ID`.
    now_min_ID ：int
        当前最小 `ID`.

    See Also
    --------
    IDGroupTable
    Table

    Notes
    -----
    * `data` 中必须存在名称为 `ID` 的域, 而且有效的 `ID` 必须是正整数. 程序内
      部通过 `ID` 判断一行是否有效, 若 ``ID <= 0``, 那么该行会被视为空白行, 调
      用 `pack` 方法时将会清除掉所有空白行.
    * `Table` 内部的 `_line_heap` 储存着表中空行的位置, 它是一个优先列队, 每次
      调用 `next_line_num` 方法的时候, 将返回下一个空白行中最小的行号.

    .. warning:: 尽管可以直接修改每行记录的 `ID`, 但强烈建议不要这么做, 即使您
       很清楚程序内部的工作机制. 程序内部通过一系列手段来记录当前表中的空白行
       号, `ID` 号, 以及行号与 `ID` 之间的对应关系, 直接修改 `ID` 容易造成系统
       内部混乱, 甚至造成有效的数据行被删除. 一般情况下无需修改 `ID`, 如需修改
        `ID` 请使用类内自带方法.
    """

    def __init__(self, data):
        super(IDTable, self).__init__(data)
        self.max_ID = np.iinfo(data['ID'].dtype).max # TODO 这里好像忘记了这个属性
        self.ID_map = {}
        self.update_ID_map()
        if self.ID_map:
            self.now_max_ID = max(self.ID_map)
            self.now_min_ID = min(self.ID_map)
        else:
            self.now_max_ID = 0
            self.now_min_ID = 0
        self._update_ID_heap()

    def update_ID_map(self):
        """更新表内的ID字典."""
        self.ID_map.clear()
        if len(self._data) == 0:
            return
        for line_num, _id in enumerate(self._data['ID']):
            if _id != 0:
                if _id in self.ID_map:
                    raise ValueError('More than one ID={}'.format(_id))
                self.ID_map[_id] = line_num

    def del_ID(self, ID):
        """删除表中编号为 `ID` 的记录, 可同时删除多个 `ID`.

        Parameters
        ----------
        ID : int, Iterable[int]
            所要删除的 `ID` 号(或由 `ID` 号组成的列表).
        """
        if isinstance(ID, Iterable):
            for n in ID:
                num = self.ID_map[n]
                self._del_a_line(num)
        else:
            num = self.ID_map[ID]
            self._del_a_line(num)

    def _del_a_line(self, line_num):
        """清空表中的一行."""
        try:
            super(IDTable,self)._del_a_line(line_num)
            heappush(self._ID_heap, line_num)
            self.ID_map.__delitem__(ID)
        except:
            raise

    def pack(self):
        """删除table中的所有空白行.

        Notes
        -----
        程序内部通过 `ID` 判断一行是否有效, 所有 ``ID <= 0`` 的行会被视为空白
        行, 调用 `pack` 方法将被清除掉.
        """
        super(IDTable,self).pack()
        self.update_ID_map()

    def _update_ID_heap(self):
        """更新表内的 `_ID_heap`"""
        id_set = set(range(self.now_min_ID, self.now_max_ID+1))
        self._ID_heap = heapify(list(id_set - set(self.ID_map)))

    def next_ID(self, update=False):
        """
        返回下一个可用的 `ID`, 当 `update` 为 `True` 时, 更新内部计数数据, 
        为False时不更新数据, 仅返回 `ID`.

        Parameters
        ----------
        update : bool
            是否更新内部计数数据, 为 `True` 时更新, 为 `False` 时不更新. 如更
            新数据, 连续两次调用该函数的返回值不同, 如不更新数据, 连续两次调用
            该函数的返回值相同. Defualt : `False`.

        Returns
        -------
        ID : int
            下一个可用`ID`.

        Notes
        -----
        确定下一个可用的 `ID` 时, 按先后顺序遵循以下原则:
        * 若 `now_min_ID` 与 `now_max_ID` 间还有未使用的 `ID`, 返回未使用 `ID`
          中的最小值.
        * 若 ``now_min_ID > 1``, 返回 ``now_min_ID - 1``.
        * 若 ``now_max_ID < max_ID``, 返回 ``now_max_ID + 1``.
        """
        if self._ID_heap:
            if update:
                next_id = heappop(self._line_heap)
            else:
                next_id = self._ID_heap[0]
        elif self.now_min_ID > 1:
            next_id = self.now_min_ID - 1
            if update:
                self.now_min_ID -= 1
        elif self.now_max_ID < self.max_ID:
            next_id = self.now_max_ID + 1
            if update:
                if self.now_max_ID == 0: # 对于初始表格max和min都为0
                    self.now_min_ID = 1
                self.now_max_ID += 1
        else:
            raise OverflowError('The number of ID has reached max_ID {}, '
                                'can\'t be bigger'.format(self.max_ID))
        return next_id

    def add_ID(self):
        """
        往表格中的下一可用行处填上下一可用 `ID`, 更新相关数据, 并返回 `ID` 号
        和行号.
        
		Returns
        -------
        ID : int
            下一个可用 `ID`.
        line_num : int
            下一个可用行号.
        """
        ID = self.next_ID(update=True)
        line_num = self.next_line_num(update=True)
        if line_num == len(self._data):
            self.expand()
        self._data[line_num]['ID'] = ID
        self.ID_map[ID] = line_num
        return ID, line_num


#TODO utility里面要有合并两个DTable的函数
#todo utility里面要有删掉、另存DTable的函数
#todo utility里还有平移ID的函数？

class IDGroupTable(Table):
    """一种用来储存交叉口内各个转弯方向的流量, 延误等信息的表, 也常称为转向表.

    `IDGroupTable` 各行间 `ID` 可重复. 一个 `ID` 对应一个交叉口, 每个交叉口内
    可有不同的转向.

    Parameters
    ----------
    data : structured array
        表中的主要数据部分, `data` 中必须存在名称为 `ID` 的域, 否则无法初始化.

    Attributes
    ----------
    names
    fields
    group_map : dict
        一个字典, 键为 `ID`, 值为该 `ID` 所对应的行号组成的列表.
    idx : ndarray
        一个 `ndarray`, 用来加快索引的速度, 仅在需要时更新, 原理同 `net.idx`.

    Notes
    -----
    * `data` 中必须存在名称为 `ID` 的域, 而且有效的 `ID` 必须是正整数. 程序内
      部通过 `ID` 判断一行是否有效, 若 ``ID <= 0``, 那么该行会被视为空白行, 调
      用 `pack` 方法时将会清除掉所有空白行.
    * `Table` 内部的 `_line_heap` 储存着表中空行的位置, 它是一个优先列队, 每次
      调用 `next_line_num` 方法的时候, 将返回下一个空白行中最小的行号.

    .. warning:: 尽管可以直接修改每行记录的 `ID`, 但强烈建议不要这么做, 即使您
       很清楚程序内部的工作机制. 程序内部通过一系列手段来记录当前表中的空白行
       号, `ID` 号, 以及行号与 `ID` 之间的对应关系, 直接修改 `ID` 容易造成系统
       内部混乱, 甚至造成有效的数据行被删除. 一般情况下无需修改 `ID`, 如需修改
        `ID` 请使用类内自带方法.
    """
    def __init__(self,data):
        super(IDGroupTable,self).__init__(data)
        self.group_map = {}
        self.update_group_map()
        self.idx = None
        self.__sorted = False

    def update_group_map(self):
        """更新表内的 `group_map` 字典"""
        self.group_map.clear()
        if len(self._data) == 0:
            return
        for line_num, ID in enumerate(self._data['ID']):
            if ID !=0:
                self._add_mem_to_group_map(ID, line_num)

    def pack(self):
        """删除table中的所有空白行.

        Notes
        -----
        程序内部通过 `ID` 判断一行是否有效, 所有 ``ID <= 0`` 的行会被视为空白
        行, 调用 `pack` 方法将被清除掉.
        """
        self.__sorted = False
        self.changed = False
        super(IDGroupTable,self).pack()
        if self.changed:
            self.update_group_map()
        else:
            self.changed = True

    def sort_and_idx(self,order=['ID','FROM','TO']):
        """将表排序，并更新转向表的索引."""
        self.pack()
        self._data.sort(order=order)
        self.idx = get_idx(self._data['ID'])
        self.update_group_map()
        self.__sorted = True

    def get_line_num(self, ID, fro, to):
        """找到相应记录所在的行号.
        
        根据所提供的 `ID`,`FROM` 和 `TO`, 寻找表中与之相匹配的哪行记录,
        并返回对应的行号. 若无法找到相应记录, 则返回 `None`.
        
        Parameters
        ----------
        ID : int
            `ID` 域的编号.
        fro : int
            `FROM` 域的编号.
        TO : int
            `TO` 域的编号.
        
        Returns
        -------
        int or None : 搜寻到的记录的行号. 若无法找到相应记录, 则返回 `None`.
        """
        try:
            line_nums = self.group_map[ID]
            aim_block = self._data[line_nums][['ID','FROM','TO']]
            want = np.array((ID,fro,to),dtype=aim_block.dtype)
            _line_num = np.nonzero(aim_block == want)
            return line_nums[_line_num[0][0]]
        except:
            return None

    def add_group(self, ID, num=1):
        """往表中添加转向记录.

        Parameters
        ----------
        ID : int
            所要添加记录的 `ID`.
        num : int, optional
            所要添加记录的数目, 默认为1.

        Returns
        -------
        line_num_list : list
            所要添加的新纪录在表中对应的行号所组成的列表.
        """
        check_int(ID)
        check_positive(ID)
        check_int(num)
        check_positive(num)
        line_num_list = []
        self.__sorted = False
        for i in range(num):
            line_num = self.next_line_num(update=True)
            line_num_list.append(line_num)
            if line_num == len(self._data):
                self.expand()
            self._data[line_num]['ID'] = ID
            self._add_mem_to_group_map(ID, line_num)
        return line_num_list

    def del_group(self, ID):
        """删除表中所有编号为 `ID` 的记录.

        Parameters
        ----------
        ID : int
            所要删除的 `ID` 号.
        """
        if ID not in self.group_map:
            print('No such ID{}'.format(ID))
        self.__sorted = False
        for line_num in self.group_map[ID]:
            self._del_a_line(line_num)

    def _add_mem_to_group_map(self, ID, line_num):
        """往 `group_map` 中添加元素.

        Parameters
        ----------
        ID : int
            所要添加元素的 `ID`.
        line_num :
            所要添加元素的行号.
        """
        if ID in self.group_map:
            self.group_map[ID].append(line_num)
        else:
            self.group_map[ID] = [line_num]

    def _del_mem_from_group_map(self, ID, line_num):
        """从 `group_map` 中删除元素.

        Parameters
        ----------
        ID : int
            所要删除元素的 `ID`.
        line_num :
            所要删除元素的行号.
        """
        self.group_map[ID].remove(line_num)
        if not self.group_map[ID]:
            self.group_map.clear(ID)

    def _del_a_line(self, line_num):
        """清空表中的一行."""
        ID = self._data[line_num]['ID']
        if ID == 0:
            return
        self.__sorted = False
        super(IDGroupTable,self)._del_a_line(line_num)
        self._del_mem_from_group_map(ID, line_num)

    def sorted(self):
        return self.__sorted
#
#
# if __name__=='__main__':
#     npdata = np.array([(5, 2.5, '是否'),
#                        (2, 3.4, '会'),
#                        (3, 5.5, '有用')],
#                       dtype={'names': ['i', 'i', 'U'],
#                              'formats': ['i4', 'f8', 'U2']})
#
#     table = Table(npdata)
#     table[1][1]=2
