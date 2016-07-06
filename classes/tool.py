# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np

__all__ = ['add_field', 'merge_two_table']


def check_int(num):
    if not isinstance(num, int):
        raise TypeError('Number must be an integer')


def check_positive(num):
    if not num > 0:
        raise ValueError('Number must be positive')


def add_field(data, names, formats):
    """Add field(s) to `data`.

    newly added fields(s) is(are) all zeros

    Parameters
    ----------
    data : structured array
    names : str, list[str]
    formats : str, list[str]

    Returns
    -------
    b : structured array
    """
    if not isinstance(data, np.ndarray):
        raise TypeError('data must be np.ndarray ')

    if data.dtype.fields is None:
        raise ValueError("data must be a structured np array")

    dtype = data.dtype.descr
    if isinstance(names, str) and isinstance(formats, str):
        dtype.append((names, formats))
    else:
        for descr in zip(names, formats):
            dtype.append(descr)

    b = np.zeros(data.shape, dtype=dtype)
    for name in data.dtype.names:
        b[name] = data[name]
    return b


# todo 效率不高（待改进）
def sort_by_first(first, second):
    """返回第二个序列各元素在第一个序列中的位置.
    """
    order = np.zeros(first.shape, dtype=np.uint16)
    for i, mem in enumerate(second):
        order[i] = np.where(first == mem)[0]
    return order


def merge_two_table(table1, table2, match_field='ID'):
    """
    用 match_field 对应合并两个表, 合并后表的行顺序与表1一致.

    Parameters
    ----------
    table1 : structured array
    table2 : structured array
    match_field : str
        连接两表的域, 必须是无重复的，且两表的要相同.

    Returns
    -------
    merge_table : np structured array
        合并后的表.
    """
    # Some checks
    foo = set(table1[match_field])
    if len(foo) != len(table1):
        print('match_fields1 should be unique!\n')
        return
    elif foo != set(table2[match_field]):
        print('two table with difference match_field!')
        return

    # Build new dtype
    names1 = list(table1.dtype.names)
    names2 = list(table2.dtype.names)
    fields1 = table1.dtype.fields
    fields2 = table2.dtype.fields
    num1 = len(names1)
    names = names1.copy()
    formats = []
    for mem in names2:
        if mem not in names1:
            names.append(mem)
    for name in names1:
        formats.append(fields1[name][0])
    for name in names[num1:]:
        formats.append(fields2[name][0])
    dtype = np.dtype({'names': names, 'formats': formats})

    # Generate merge_table
    merge_table = np.zeros((len(foo),), dtype=dtype)
    for name in names1:
        merge_table[name] = table1[name]
    new_order2 = sort_by_first(table2[match_field], table1[match_field])
    # table2 with the same order with table1 in match_field, no duplicated names
    new_table2 = table2[new_order2][names[num1:]]
    for name in names[num1:]:
        merge_table[name] = new_table2[name]
    return merge_table
