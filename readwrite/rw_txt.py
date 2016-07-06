# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import numpy as np
import os
import re

D_ENCODE = 'utf-8'


def skip(f, num):
    """skip num lines in f"""
    for line in range(num):
        f.readline()


# def find_effect_line(ID_column):
#     """
#     返回有效的行的序号
#     """
#     return np.where((ID_column > 0) & (ID_column <= 65536))
#
#
# def pack_data(data):
#     """
#     除掉table中编辑过程中产生的无效的行
#     """
#     effect_line = find_effect_line(data['ID'])
#    return np.array(data[effect_line])

def load_bin(file):
    path = os.path.splitext(file)[0]
    try:
        dtype = get_bin_format(path + '.dcb')
        data = np.fromfile(file, dtype=dtype)
        return data
    except BaseException as e:
        raise


def get_bin_format(file):
    # for consistent with TC's format
    trans_dic = {'I': 'i', 'R': 'f','F':'f', 'C': 'a','S':'S'}  # 这里改成全局的？
    names = []
    formats = []
    try:
        with open(file, 'r') as f:
            for line in f:
                if not line.startswith('"'):
                    continue
                else:
                    line_mem = line.split(',')
                    names.append(line_mem[0].strip('"'))
                    formats.append(trans_dic[line_mem[1]] + line_mem[3])
    except FileNotFoundError as e:
        raise e
    except KeyError as e:
        raise ('Unknow Key word {} in {}'.format(e,file))
    dtype = np.dtype({'names': names, 'formats': formats})
    return dtype


def load_point_geo_txt(file, sep=',', header=0, fooder=0, encoding='utf-8',
                       ptype='LONG_LAT'):
    """Read point geographic data from txt/csv file.

    Parameters
    ----------
    file : str
        要读取的文件路径.
    sep : string
        分隔符
    header : integer
        开头几行不要.
    fooder : integer
        结尾几行不要.
    encoding : 编码方式
        默认为utf-8,中文系统常用到gbk.
    ptype : {'LONG_LAT', 'XY'}, optional
        指明地理文件中的是经纬度还是坐标, 是'LONG_LAT'则返回值中 `field`
        为 ``['ID', 'X', 'Y', 'LONG', 'LAT']``, 其中'X', 'Y' 为空. 是'XY'
        则返回值中 `field` 为 ``['ID', 'X', 'Y']``. Default : 'LONG_LAT'.

    Return
    ------
    structured array
    """
    if ptype == 'LONG_LAT':
        names = ['ID', 'X', 'y', 'LONG', 'LAT']
        formats = ['u2', 'f8', 'f8', 'f8', 'f8']
        x_pos = 'LONG'
        y_pos = 'LAT'
    elif ptype == 'XY':
        names = ['ID', 'X', 'y']
        formats = ['u2', 'f8', 'f8']
        x_pos = 'X'
        y_pos = 'y'
    else:
        raise ValueError("Wrong position-type, use 'XY' or 'LANG_LAT'")
        return
    with open(file, 'r', encoding=encoding) as f:
        file = f.readlines()
        num = len(file)
    data = np.zeros((num - header - fooder,),
                    dtype=np.dtype({'names': names, 'formats': formats}))
    for idx, line in enumerate(file[header: (num - fooder)]):
        a_record = line.strip().split(sep)
        data[idx]['ID'] = a_record[0]
        data[idx][x_pos] = a_record[1]
        data[idx][y_pos] = a_record[2]
    return data


def load_line_geo_txt(file, sep=',', header=0, fooder=0, encoding='utf-8',
                      ptype='LONG_LAT'):
    """Read line geographic data from txt/csv file

    Parameters
    ----------
    file : str
        要读取的文件路径.
    sep : string
        分隔符.
    header : integer
        开头几行不要.
    fooder : integer
        结尾几行不要.
    encoding : 编码方式
        默认为utf-8, 中文系统常用到gbk.
    ptype : {'LONG_LAT', 'XY'}, optional
        指明地理文件中的是经纬度还是坐标,
        是'LONG_LAT'则返回字典值中结构数组的field为X', 'y', 'LONG', 'LAT',
        是'XY' 则返回字典值中结构数组的field为'X', 'y'.

    Return
    ------
    A dictionary keyed by line's ID, stores coordinates or LONG_LAT
    in numpy structured array
    """
    if ptype == 'LONG_LAT':
        names = ['ID', 'X', 'y', 'LONG', 'LAT']
        formats = ['i2', 'f8', 'f8', 'f8', 'f8']
        x_pos = 'LONG'
        y_pos = 'LAT'
    elif ptype == 'XY':
        names = ['ID', 'X', 'y']
        formats = ['i2', 'f8', 'f8']
        x_pos = 'X'
        y_pos = 'y'
    else:
        print('wrong dtype')
        return
    data = {}
    dtype = np.dtype({'names': names, 'formats': formats})

    with open(file, 'r', encoding=encoding) as f:
        file = f.readlines()

    num = len(file)
    for i, line in enumerate(file[header: (num - fooder)]):
        a_record = line.strip().split(sep)
        num = int(a_record[1])
        _pos = np.array(a_record[2:], dtype=np.float64).reshape((num, 2))
        pos = np.zeros((num,), dtype=dtype)
        pos[x_pos] = _pos[:, 0]
        pos[y_pos] = _pos[:, 1]
        data[int(a_record[0])] = pos

    return data


# todo 对于有format文件的情况还没处理
def load_txt_table(file, sep='\s*,?\s*', skip_header=0, skip_footer=0,
                   encoding=D_ENCODE, names=None, formats=None,
                   missing_values=None, filing_values=None, fast_mode=False):
    """从txt/csv文件读取表格数据

    Parameters
    ----------
    file : str
        要读取的文件路径
    sep : regex, optional
        分隔符, 默认的分隔符为一个英文逗号(包括逗号周边的空白符)或仅空白符.
    skip_header : integer, optional
        开头几行不要.
    skip_footer : integer, optional
        结尾几行不要.
    encoding : 编码方式
        默认采用全局设置, 中文系统常用到gbk.
    names : 0/1/list, optional
        为0与list时的效果同formats. 为1时则从file文件的第一个有效行读取域的名称.
    formats : 0/list, optional
        data每列对应的数据格式, 为0时先寻找是否存在与file配对的格式(*.fmt)文件,
        若存在则从格式文件中读取格式, 若不存在则自动确定格式.
        自动确定格式时, 整形全变成np.int32, 浮型全变成np.float64, 其余的都转成
        np.unicode. 为list时, list中的每个元素分别表示data每列的格式.
    missing_values : list/tuple/set, optional
        列在miss_value里的项, 视为缺失值. Default: ``set('')``
    filing_values : dict, optional
        各数据类型缺失时的替换值, 仅指明与默认不同的项即可, 未指明的采用默认值.
        Default: ``{'i': 0, 'f': np.nan, 'u': 0, 'b': False, 'U': ''}``
    fast_mode : bool, optional
        为True时不对缺失值, 空格, 字符串两边的引号等进行替换, 当数据很大时速度较快,
        但未经检查的数据更可能出现错误, 当数据以 native data 的形式进行读取时此项
        不起作用, 默认为False.

    Return
    ------
    data : numpy structured array

    Notes
    -----
    若显式地提供names, formats, 其优先级高于与数据同名的格式文件(*.fmt)文件中的格
    式.当不采用格式文件中的formats时, 数据被视为 "非原生数据" 导入时会检查其是否含
    有缺失值, 空格等, 并进行替换. 当采用格式文件中的formats时,数据被视为"原生数据",
    会直接导入而不进行检查, 速度较快.
    """
    # todo docstr 中 names和formats的0应该改为None或者取消.
    if missing_values is None:
        missing_values = {''}
    else:
        missing_values = set(missing_values)
    _filing_values = {'i': 0, 'f': np.nan, 'u': 0, 'b': False, 'U': ''}
    if filing_values is None:
        filing_values = _filing_values
    else:
        _filing_values.update(filing_values)
        filing_values = _filing_values
    fmt_dict = None
    native_data = False
    sep = re.compile(sep)

    # Read whole file，get needed line, split each line to list.
    with open(file, 'r', encoding=encoding) as f:
        data = f.readlines()
    if names == 1:
        names = sep.split(data[skip_header].strip())
        skip_header += 1
    num = len(data)
    data = data[skip_header: (num - skip_footer)]
    for i in range(len(data)):
        data[i] = sep.split(data[i].strip())
    data_len = len(data)
    rec_len = len(data[0])

    # If need read format file, then try to read it
    if names is None or formats is None:
        path = os.path.splitext(file)[0]
        if os.path.exists(path + '.fmt'):
            fmt_dict = None  # todo 加个函数，从fmt里读回names
            native_data = True

    # Get default names
    if names is None and fmt_dict is None:
        names = ['f' + str(i) for i in range(rec_len)]

    # Auto format
    if formats is None and fmt_dict is None:
        formats = [None for i in range(rec_len)]
        for j in range(rec_len):
            if formats[j] is None:
                formats[j] = get_mem_format(data, 0, j, missing_values)
        native_data = False

    if not len(names) == len(formats) == rec_len:
        raise ValueError("'names' 或 'formats' 的个数与数据不一致!")

    # Check each member, replace missing value etc.
    if not native_data and not fast_mode:
        check_dict = get_check_dict()
        for j in range(rec_len):
            char_len = [0]  # To mark the max length of unicode char.
            format_str = np.dtype(formats[j]).kind
            check = check_dict[format_str]
            filing_value = filing_values[format_str]
            for i in range(data_len):
                check(data, i, j, missing_values, filing_value, char_len)
            if char_len[0] != 0:
                formats[j] = formats[j][0] + str(char_len[0])

    # Transform data to np.array with corresponding names and formats.
    if not isinstance(formats, list):
        formats = fmt_dict['formats']
    if not isinstance(names, list):
        names = fmt_dict['names']
    for i in range(data_len):
        data[i] = tuple(data[i])
    data = np.array(data, dtype={'names': names, 'formats': formats})
    return data


def get_check_dict():
    """得到一个用来矫正问题数据的字典.

    For all `int` and `float`, replace missing value with filling value.
    For `unicode char`, replace space with '_', strip quotes and
    mark the max length of unicode char.

    Returns
    -------
    dict : key为各种数据类型代号的首字母, value为对应的操作函数.
    """

    def deal(data, i, j, missing_values, filing_value, char_len):
        if data[i][j] in missing_values:
            data[i][j] = filing_value

    def deal_U(data, i, j, missing_values, filing_value, char_len):
        foo = data[i][j]
        if foo in missing_values:
            data[i][j] = filing_value
        if '"' in foo:
            data[i][j] = data[i][j].strip('"')
        if "'" in foo:
            data[i][j] = data[i][j].strip("'")
        if ' ' in foo:
            data[i][j] = data[i][j].replace(' ', '_')
        now_len = len(data[i][j])
        if char_len[0] == 0:
            char_len[0] = 1
        if now_len > char_len[0]:
            char_len[0] = now_len

    return {'i': deal, 'f': deal, 'u': deal, 'b': deal, 'U': deal_U}


def get_mem_format(data, i, j, missing_vale):
    """ 确定 ``data[i][j]`` 元素的数据格式.

    整形全视作 `np.int32`, 浮型全视作 `np.float64`, 其余视作 `np.unicode`.
    若当前数据为缺失值, 则根据下一行同位置元素确定, 若整列全为缺失值, 则视作
    `np.int32`.

    Returns
    -------
    'i4', 'f8' or 'U'
    """
    # 如果当前项为缺失值, 跳到下一列, 全为缺失值视为 np.int32.
    mem = data[i][j]
    max_i = len(data) - 1
    while mem in missing_vale:
        if i < max_i:
            i += 1
        else:
            return 'i4'
        mem = data[i][j]

    try:
        int(mem)
        return 'i4'
    except ValueError:
        try:
            float(mem)
            return 'f8'
        except ValueError:
            return 'U'
