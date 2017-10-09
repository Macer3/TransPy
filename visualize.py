# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
from transpy.gui.test_double import road
from transpy.gui.test_plot import load_test_data
from transpy.compute.assignment import *
import transpy as tp
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.colors as colors
import matplotlib.cm as cmx


point_table, line_data, node_table, link_table, turn_table, net, matrix = load_test_data()

cfg = AssignConfig()
cfg.method = 'UE'
cfg.time_field = 'times'
cfg.capacity_field = 'capacity'
cfg.convergence = 0.001
cfg.max_iteration = 100
cfg.preload_field = 'flow'
cfg.turn_delay_type = 'all'
cfg.print_frequency = 0

link_flow, turns_flow, summary = user_equilibrium(net, matrix, link_table,
                                                  cfg)
all_flow  = np.zeros(link_flow.shape, dtype = ({'names':['ID','AB_FLOW','BA_FLOW','AB_C/V','BA_C/V'],
                                               'formats':[ID_TYPE, 'f8','f8','f8','f8']}))
all_flow['AB_FLOW'] = link_flow['AB_FLOW'] + link_table['AB_flow']
all_flow['BA_FLOW'] = link_flow['BA_FLOW'] + link_table['BA_flow']
all_flow['BA_C/V'] = all_flow['BA_FLOW'] / link_table['capacity']
all_flow['AB_C/V'] = all_flow['AB_FLOW'] / link_table['capacity']
all_flow['ID'] = link_flow['ID']
all_flow = tp.IDTable(all_flow)

def draw_flow(line_data, link_flow, colormap='viridis', scale=0.00005):
    plt.close('all')
    plt.ion()
    fig = plt.figure(figsize=[9,6])
    fig.set_facecolor('w')
    axes = fig.add_axes([0, 0, 1, 1])
    axes.axis('off')
    cm = plt.get_cmap(colormap,30)
    cNorm = colors.NoNorm(vmin=0,vmax=1.5)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
    ft = np.linspace(0,1.5, 15)
    scalarMap.set_array(ft)


    for i in range(link_flow.shape[0]):
        ID = link_flow[i]['ID']
        xdata = line_data[ID]['LONG']
        ydata = line_data[ID]['LAT']
        if link_flow[i]['ID'] > 86:
            continue
        else:
            line = Line2D(xdata, ydata, linewidth=0.5, color='k')
        j = link_flow.ID_map[ID]

        colorVal = scalarMap.to_rgba(link_flow[j]['AB_C/V'])
        AB_flow = link_flow[j]['AB_FLOW']
        if  AB_flow != 0:
            AB = road(xdata, ydata, -AB_flow, scale=scale, color=colorVal)
            axes.add_patch(AB)

        colorVal = scalarMap.to_rgba(link_flow[j]['BA_C/V'])
        BA_flow = link_flow[j]['BA_FLOW']
        if BA_flow != 0:
            BA = road(xdata, ydata, BA_flow, scale=scale, color=colorVal)
            axes.add_patch(BA)
        axes.add_line(line)

    cbar = fig.colorbar(scalarMap)
    cbar.set_ticks(np.linspace(0,30,4))  
    cbar.set_ticklabels( ('0', '0.5', '1', '1.5'))  
    axes.axis([-1.3008, -1.0992, 0.046525,  0.213475])
#    axes.axis('equal')

if __name__ == '__main__':
    draw_flow(line_data, all_flow, colormap='jet', scale=0.0000005)

