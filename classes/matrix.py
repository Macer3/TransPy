# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np


def zero_matrix(rows, cols, dtype=np.float64):
    """Generate an all-zero Matrix.

    Parameters
    ----------
    rows : int
        number of rows of the Matrix.
    cols : int
        number of columns of the Matrix.        .
    dtype : data-type, optional
        The desired data-type for the array, e.g., `numpy.int32`.
        Default is `numpy.float64`.

    Returns
    -------
    Matrix : An all-zero Matrix with the given rows, cols and dtype.
    """
    data = np.zeros((rows, cols), dtype)
    return Matrix(data)


class Matrix(object):
    """矩阵, 用来表示多个点两两之间的联系数据.

    通常该类用来表示 OD(origin-destination) 矩阵, 每行表示一个出发地, 每列表示
    一个目的地, 第 i 行第 j 列的元素表示从 i 地到 j 地的交通量(通常表示交通量,
    也可用于表示其他数据).

    矩阵类由3个部分组成, `data` 为一矩阵的主体部分, `row_idx` 表示 `data` 中的
    每一行对应在 `Table` 中的 `ID`. `col_idx` 表示 `data` 中的每一列对应在
    `Table` 中的 `ID`. 目前 `ID` 的范围限制在 [1,65535] 之间.

    Parameters
    ----------
    data : array_like
        矩阵数据的主体部分. 数据必须为 `ndarray` 或者能转换为 `ndarray` 的
        类型. 且转换后的 `ndarray` 必须是2维的, 数值类型的, 否则将会抛出错误.

    Attributes
    ----------
    row_idx : ndarray
        矩阵每一行对应的 `Table` 中的 `ID` 号, 其长度和矩阵的行数相等. 初始值为
        1~行数的序列.
    col_idx : ndarray
        矩阵每一列对应的 `Table` 中的 `ID` 号, 其长度和矩阵的列数相等. 初始值为
        1~列数的序列.
    data : ndarray
        矩阵的数据主体部分.
    shape ：tuple
        矩阵的形状.
    dtype : data-type
        矩阵中的数据类型.

    Notes
    -----
    `Matrix` 类与 numpy 中的 `matrix` 类完全不同. `matrix` 类继承自 `ndarray`,
    可以直接对其应用 `ndarray` 的各类方法. 而 `Matrix` 类只是将一个 `ndarray`
    作为一个组成部分, 如果想对其应用 numpy 中的各类函数, 需对 ``Matrix.data``
    进行操作.
    """

    def __init__(self, data):
        self._row_idx = np.array([], dtype=np.uint16)
        self._col_idx = np.array([], dtype=np.uint16)
        self._data = None
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        """
        更新 `Matrix` 类中的 `_data`. 如果新 `data` 与原 `_data` 的行或列相等,
        则保留原 `row_idx` 或 `col_idx`; 若不等, 将 `row_idx` 或 `col_idx`
        设为初始值.

        Parameters
        ----------
        data : array_like
        矩阵数据的主体部分. 数据必须为 `ndarray` 或者能转换为 `ndarray` 的
        类型. 且转换后的 `ndarray` 必须是2维的, 数值类型的, 否则将会抛出错误.
        """
        try:
            np.asarray(data)
        except:
            raise TypeError("Cant't convert data to np.ndarray.")
        if not data.dtype.isbuiltin:
            raise TypeError("{} is unacceptable, use int or float type.".
                            format(data.dtype))
        if data.ndim != 2:
            raise ValueError("Dimension of Matrix's data must be 2.")

        self._data = data
        row_num, col_num = data.shape
        if row_num != len(self._row_idx):
            self.row_idx = np.arange(1, row_num + 1, 1, dtype=np.uint16)
        if col_num != len(self._col_idx):
            self.col_idx = np.arange(1, col_num + 1, 1, dtype=np.uint16)

    @property
    def row_idx(self):
        return self._row_idx

    @row_idx.setter
    def row_idx(self, idx):
        idx = self._check_idx(idx)
        rows = self._data.shape[0]
        if idx.shape != (rows,):
            raise ValueError("row_idx's shape is not {}".format((rows,)))
        self._row_idx = idx

    @property
    def col_idx(self):
        return self._col_idx

    @col_idx.setter
    def col_idx(self, idx):
        idx = self._check_idx(idx)
        cols = self._data.shape[1]
        if idx.shape != (cols,):
            raise ValueError("col_idx's shape is not {}".format((cols,)))
        self._col_idx = idx

    @staticmethod
    def _check_idx(idx):
        """检查索引是否在[1,65535]内."""
        max_idx = max(idx)
        min_idx = min(idx)
        if max_idx > 65535 or min_idx < 0:
            raise ValueError("index's range out of [1,65535]")
        return np.asarray(idx, dtype=np.uint16)

    @property
    def shape(self):
        return self._data.shape

    @property
    def dtype(self):
        return self._data.dtype

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
