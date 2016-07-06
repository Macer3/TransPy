# -*- coding: utf-8 -*-
import os.path
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

# np_dirs = numpy.get_include

ext = [
    # Extension("shortest_way",
    #           ["shortest_way.pyx"],
    #           include_dirs=[numpy.get_include]),
    Extension("heap",
              ["heap.pyx"],
              include_dirs=[numpy.get_include])
]

setup(name='compute',
      version='0.1',
      ext_modules=cythonize(ext)
      )
