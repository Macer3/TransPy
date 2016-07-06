# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import nose.tools as nt
import numpy as np
import transpy as tp
from heapq import heapify

npdata = np.array([(1, 2.5, '是否'),
                   (2, 3.4, '会'),
                   (3, 5.5, '有用')],
                  dtype={'names': ['i', 'f', 'U'],
                         'formats': ['i4', 'f8', 'U2']})


class TestTable():
    def setup(self):
        self.table = tp.Table(npdata.copy())

    def test_names(self):
        t = self.table
        nt.assert_equal(t.names, ('i', 'f', 'U'))

    def test_len(self):
        nt.assert_equal(len(self.table), 3)

    def test_get(self):
        U = self.table[1]['U']
        f = self.table['f'][1]
        nt.assert_equal(U, '会')
        nt.assert_equal(f, 3.4)

    def test_setitem(self):
        self.table[1]['U'] = '可以'
        nt.assert_equal(self.table[1]['U'], '可以')

    def test_del_line(self):
        # del line
        self.table.del_line(2)
        nt.assert_equal(self.table[2][0], 0)
        nt.assert_equal(self.table._line_heap, [2])
        # del lines
        self.table.del_line(range(3))
        np.testing.assert_equal(self.table._data,
                                np.zeros((3,), self.table._data.dtype))

        nt.assert_raises(IndexError, self.table.del_line, 4)

    def test_expand(self):
        self.table.expand(10)
        nt.assert_equal(len(self.table), 13)
        nt.assert_equal(self.table._line_heap, list(range(3, 13)))

    def test_pack(self):
        self.table.del_line(2)
        self.table.pack()
        nt.assert_equal(self.table._line_heap, [])
