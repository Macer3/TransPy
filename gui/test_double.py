# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
from __future__ import division
import numpy
from matplotlib import pyplot, patches


def road(x, y, w, scale=0.005, **kwargs):
    # Makes sure input coordinates are arrays.
    x, y = numpy.asarray(x, dtype=float), numpy.asarray(y, dtype=float)
    # Calculate derivative.
    dx = x[2:] - x[:-2]
    dy = y[2:] - y[:-2]
    dy_dx = numpy.concatenate([
        [(y[1] - y[0]) / (x[1] - x[0])],
        dy / dx,
        [(y[-1] - y[-2]) / (x[-1] - x[-2])]
    ])
    # Offsets the input coordinates according to the local derivative.
    offset = -dy_dx + 1j
    offset =  w * scale * offset / abs(offset)
    y_offset = y + w * scale
    #
    AB = zip(
        numpy.concatenate([x + offset.real, x[::-1]]),
        numpy.concatenate([y + offset.imag, y[::-1]]),
    )
    p = patches.Polygon(list(AB), **kwargs)

    # Returns polygon.
    return p


if __name__ == '__main__':
    # Some plot initializations
    pyplot.close('all')
    pyplot.ion()

    # This is the list of coordinates of each point
    x = [0, 1, 2, 3, 4]
    y = [1, 0, 0, -1, 0]

    # Creates figure and axes.
    fig, ax = pyplot.subplots(1,1)
    ax.axis('equal')
    center_line, = ax.plot(x, y, color='k', linewidth=2)

    AB = road(x, y, 20, color='g')
    BA = road(x, y, -30, color='r')
    ax.add_patch(AB)
    ax.add_patch(BA)
    a=input()