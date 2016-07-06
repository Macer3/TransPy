# -*- coding: utf-8 -*-
"""
@author: Zhanhong Cheng
"""
import os
import platform
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import transpy as tp
from transpy.test.load_data import load_test_data
from transpy.gui.tableview import *
from  transpy.gui.assign_ui import assign_dialog
import matplotlib

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from transpy.readwrite.rw_txt import *
import transpy as tp
import os
from transpy.compute.assignment import all_or_nothing, user_equilibrium, \
    AssignConfig
import numpy as np

__version__ = "0.0.1"

DIR = os.path.split(os.path.realpath(__file__))[0]


path = "D:\Documents\PythonS\\transpy\\test\\transpy\\test\data\Weihai_City\\"


def load_raw_test_data():
    line_table = load_txt_table(path + 'street.txt',
                                names=['ID', 'LENGTH', 'DIR', 'Layer',
                                       'Handle', 'times', 'speed', 'capacity',
                                       'AB_flow', 'BA_flow', 'names'],
                                formats=['i4', 'f4', 'u1', 'U1', 'i4', 'f8',
                                         'i4', 'i4', 'i4', 'i4', 'U16'],
                                encoding='gbk')
    accurate_line_data = load_bin(path + 'line.bin')
    line_table['times'] = accurate_line_data['time']
    del accurate_line_data

    point_table = load_txt_table(path + 'Endpoints.txt',
                                 names=['ID', 'LONG', 'LAT', 'index'],
                                 formats=['u2', 'f8', 'f8', 'u8'],
                                 encoding='gbk')

    point_data = load_point_geo_txt(path + 'node.geo',
                                    ptype='LONG_LAT', encoding='gbk')

    point_table.sort(order=['ID'])
    point_data.sort(order=['ID'])
    point_table['LONG'] = point_data['LONG']
    point_table['LAT'] = point_data['LAT']

    line_data = load_line_geo_txt(path + 'street.geo',
                                  ptype='LONG_LAT', encoding='gbk')
    link_data = tp.geo.build_point_line_connection(point_data,
                                                   line_data,
                                                   ptype='LONG_LAT')
    link_data = tp.merge_two_table(link_data, line_table)

    turn_table = load_txt_table(path + '\\turn.txt',
                                names=['ID', 'FROM', 'TO', 'DELAY'],
                                formats=['u2', 'u2', 'u2', 'f8'],
                                filing_values={'f': np.inf})
    matrix_table = load_bin(path + 'matrix.bin')
    matrix = tp.Matrix(matrix_table['pre'].copy().reshape((50, 50)))
    matrix.row_idx = matrix_table['O'][0::50]
    matrix.col_idx = matrix_table['D'][0:50]
    matrix._data = np.asarray(matrix._data, dtype=np.float64)

    return point_table, line_data, link_data, turn_table, matrix


def load_test_data():
    point_table, line_data, link_data, turn_table, matrix = load_raw_test_data()
    node_table = tp.IDTable(point_table)
    link_table = tp.IDTable(link_data)
    if turn_table is not None:
        turn_table = tp.IDGroupTable(turn_table)
    net = tp.Net(link_table,
                 fields=['ID', 'LENGTH', 'DIR', 'capacity', 'times',
                         'AB_flow', 'BA_flow'],
                 turn_table=turn_table)
    return point_table, line_data, node_table, link_table, turn_table, net, matrix


point_table, line_data, node_table, link_table, turn_table, net, matrix = load_test_data()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.var_dict = {
                   'node_table': node_table,
                   'link_table': link_table,
                   'turn_table': turn_table,
                   'net': net,
                   'matrix': matrix}
        self.opened = {}
        self.dirty = False
        self.filename = None
        self.createActions()
        self.createMenus()
        # self.createDockWindows()
        self.createToolBars()

        self.setWindowTitle("TransPy")
        # self.resize(600, 400)
        self.createStatusBar()
        # _, self.link_table, _, net, matrix = load_test_data()

        self.main_frame = QWidget()
        self.fig = Figure()
        self.fig.set_facecolor('w')
        self.axes = self.fig.add_axes([0, 0, 1, 1])
        self.axes.axis('off')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocus()
        self.canvas.mpl_connect('pick_event', self.onpick)


        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        # self.mpl_toolbar._actions

        vbox = QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.canvas)  # the matplotlib canvas
        # vbox.addWidget(self.mpl_toolbar)
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        self.on_draw()

    def onpick(self,event):
        art = event.artist
        if isinstance(art, Line2D):
            gid = art.get_gid()
            print(gid)
            if 'link_table' not in self.opened:
                self.openVar('link_table')
            line = self.var_dict['link_table'].ID_map[gid]
            self.opened['link_table'].dataTableView.selectRow(line)
        return True

    def openVar(self,name):
        """将相应的变量在表格里面打开."""
        if name in self.opened:
            self.opened[name].setFocus()
            return True

        table = TableEditor(self.var_dict[name], name, self)
        table.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
                              | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, table)
        table.destroyed.connect(self.dele)
        self.opened[name] = table
        return True

    def dele(self):
        name = self.sender().windowTitle()
        del self.opened[name]
        return True

    def createDockWindows(self):
        dock = QDockWidget("Customers", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.customerLabel = QLabel(dock)
        dock.setWidget(self.customerLabel)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def createActions(self):
        self.fileNewAct = QAction(QIcon(DIR + '/images/fileopen.png'),
                                  "打开(&O)", self, shortcut=QKeySequence.Open,
                                  statusTip="Open new file",
                                  triggered=self.fileOpen)

        self.assginAct = QAction(QIcon(DIR + '/images/assign.png'),
                          "交通分配(&A)", self, statusTip="Traffic Assignment",
                          triggered=self.assignment)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("文件(&F)")
        self.fileMenu.addAction(self.fileNewAct)
        self.toolMenu = self.menuBar().addMenu("工具(&T)")
        self.toolMenu.addAction(self.assginAct)
        self.helpMenu = self.menuBar().addMenu("帮助(&H)")
        self.helpMenu.addAction('&About',self.about)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.fileNewAct)
        self.fileToolBar.addAction(self.assginAct)
        # 初始化变量名列表.
        self.varBox = QComboBox(self)
        self.varBox.setEditable(True)
        self.fileToolBar.addWidget(self.varBox)
        self.varBox.currentIndexChanged.connect(
            lambda : self.openVar(self.varBox.currentText()))
        self.update_var()
        # self.varBox.activated.connect(self.update_var)

    def about(self):
        QMessageBox.about(self, "About",
        """交通分配软件TransPy 0.0.1""")


    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def fileOpen(self):
        dir = DIR if DIR is not None else "."
        formats = ['*.txt', '*.csv']
        file = QFileDialog.getOpenFileName(self,
                                           "TransPy - Open file", dir,
                                           "Image files (%s)" % " ".join(
                                               formats))
        if file:
            self.loadFile(file)
        else:
            return False

    def assignment(self):
        assign_ui = assign_dialog(self)
        assign_ui.exec_()
        self.update_var()
        return True

    def loadFile(self, file):
        table = tp.load_txt_table(file[0])
        self.customerLabel.setText(str(table[0]))

    def on_draw(self):
        """画道路图象"""
        for i in range(link_table.shape[0]):
            ID = link_table[i]['ID']
            xdata = line_data[ID]['LONG']
            ydata = line_data[ID]['LAT']
            if link_table[i]['speed'] == 100000:
                line = Line2D(xdata, ydata, linewidth=2, linestyle='--',
                              color='gray',picker=5)
            else:
                line = Line2D(xdata, ydata, linewidth=2, linestyle='-',
                              color='b',picker=5)
            line.set_gid(ID)
            self.axes.add_line(line)

        # ID = point_table[point_table['index']!=0][ID]
        xdata = point_table['LONG']
        ydata = point_table['LAT']
        self.axes.scatter(xdata, ydata, marker='^', edgecolors='r',
                          facecolor='none')
        self.axes.axis('auto')
        self.axes.axis('equal')

    def update_var(self):
        """更新变量名框里面的变量."""
        self.varBox.currentIndexChanged.disconnect()
        self.varBox.clear()
        self.varBox.addItems(list(self.var_dict))
        self.varBox.currentIndexChanged.connect(
            lambda : self.openVar(self.varBox.currentText()))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TransPy")
    app.setWindowIcon(QIcon(DIR + "/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
