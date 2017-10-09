# TransPy
An open source traffic planning software.

A software developed in my undergraduate thesis. Although I don't have time and incentive to maintain or further develop it, it can currently be used to carry out some interesting studies, the highlights of the software are:
- Numpy array and Cython make it fast enough for large-scale  network assignment.
- Turn delay/prohibitive can be taken into account.
- Can be wirelessly connected to other python packages for further analysis.
- UE and AON are achieved (other methods of assignment need more coding).

## Example
``` Python
%matplotlib inline
from transpy.test.demo import load_test_data
from transpy.gui.visualize import draw_flow
from transpy.compute.assignment import *
import transpy as tp

# Load data
point_table, line_data, node_table, link_table, turn_table, net, matrix = load_test_data()

# Assignment parameter configration
cfg = AssignConfig()
cfg.method = 'UE'
cfg.time_field = 'times'
cfg.capacity_field = 'capacity'
cfg.convergence = 0.001
cfg.max_iteration = 100
cfg.preload_field = 'flow'
cfg.turn_delay_type = 'all'
cfg.print_frequency = 0

# Sensitivity analysis when demand level is multiplied by different multiplier. 
def demo(multiplier=1):
    matrix1 = tp.Matrix(matrix._data)
    matrix1._data= matrix1._data*multiplier
    link_flow, turns_flow, summary = user_equilibrium(net, matrix1, link_table, cfg) # UE assignment
    
    all_flow  = np.zeros(link_flow.shape, dtype = ({'names':['ID','AB_FLOW','BA_FLOW','AB_C/V','BA_C/V'],
                                                    'formats':[ID_TYPE, 'f8','f8','f8','f8']}))
    all_flow['AB_FLOW'] = link_flow['AB_FLOW'] + link_table['AB_flow']
    all_flow['BA_FLOW'] = link_flow['BA_FLOW'] + link_table['BA_flow']
    all_flow['BA_C/V'] = all_flow['BA_FLOW'] / link_table['capacity']
    all_flow['AB_C/V'] = all_flow['AB_FLOW'] / link_table['capacity']
    all_flow['ID'] = link_flow['ID']
    all_flow = tp.IDTable(all_flow)
    
    draw_flow(line_data, all_flow, colormap='jet', scale=0.0000005)

# Use IPython to interactively analyze
from IPython.html.widgets import interact
interact(demo, multiplier=(0.5,1.5));
```
![image](https://github.com/Macer3/TransPy/blob/master/test/data/multiply_demo.gif)
