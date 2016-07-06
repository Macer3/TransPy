# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np
from transpy.classes import convert as cv


class Net(object):
    def __init__(self, street_table, fields, turn_table=None):
        self._data, self.idx, self.r_idx, self.trace = \
            cv.get_net_data(street_table._data, fields)
        self.turn_table = None
        if turn_table:
            cv.update_net_flag(self, turn_table)
            # todo 直接给turning_table._data会更好吗？
            # todo net 的idx等东西应该变成只读的
            self.turn_table = turn_table

    @property
    def names(self):
        """返回表中数据各列的域名."""
        return self._data.dtype.names

    @property
    def dtype(self):
        """表中数据各列的数据类型信息."""
        return self._data.dtype

    def __len__(self):
        return self._data.shape[0]

    def __getitem__(self, key):
        return self._data[key]

    @property
    def shape(self):
        """表中数据各列的域名及其数据类型组成的字典."""
        return self._data.shape


def next_node_line():
    pass


def pre_node_line():
    pass


def next_node_ID():
    pass


def pre_node_ID():
    pass
