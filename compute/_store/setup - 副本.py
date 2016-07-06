# -*- coding: utf-8 -*-
# setup file for the early shortest_way.pyx

import os.path

base_path = os.path.abspath(os.path.dirname(__file__))


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration, get_numpy_include_dirs
    from Cython.Build import cythonize

    config = Configuration('compute', parent_package, top_path)
    #config.add_data_dir('tests')

    # This function tries to create C files from the given .pyx files.  If
    # it fails, try to build with pre-generated .c files.
    # cython(['_spath.pyx'], working_path=base_path)
    # cython(['_mcp.pyx'], working_path=base_path)
    # cython(['heap.pyx'], working_path=base_path)
    cythonize('heap.pyx')
    cythonize('shortest_way.pyx')

    config.add_extension('heap', sources=['heap.c'],
                         include_dirs=[get_numpy_include_dirs()])
    config.add_extension('shortest_way', sources=['shortest_way.c'],
                         include_dirs=[get_numpy_include_dirs()])
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(description='Algorithms in graph and traffic',
          **(configuration(top_path='').todict())
          )
