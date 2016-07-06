
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

__version__ = "0.0.1"
_, link_table, _, net, matrix = load_test_data()

DIR = os.path.split(os.path.realpath(__file__))[0]


class TableModel(QAbstractTableModel):
    """ DataFrame Table Model"""
    def __init__(self, structured_array, format="%.3g", parent=None):
        super(TableModel,self).__init__(parent)
        self.array = structured_array
        self.tb_header = structured_array.dtype.names
        self._format = format

        self.total_rows = self.array.shape[0]
        self.total_cols = self.array.names.__len__()

    # TODO 要把format改成每列的
    def get_format(self):
        """Return current format"""
        # Avoid accessing the private attribute _format from outside
        return self._format

    def set_format(self, format):
        """Change display format"""
        self._format = format
        self.reset()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Set header data"""
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.tb_header[section]
        if orientation == Qt.Vertical:
            return section
        else:
            return None

    def data(self, index, role=Qt.DisplayRole):
        """Cell content"""
        if not index.isValid():
            return None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            column = index.column()
            row = index.row()
            value = self.array[row][column]
            if isinstance(value, float):
                return self._format % value
            else:
                return str(value)
        return None

    def flags(self, index):
        """Set flags"""
        if self.tb_header[index.column()] == 'ID':
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                            Qt.ItemIsEditable)

    def setData(self, index, value, role=Qt.EditRole, change_type=None):
        """Cell content change"""
        column = index.column()
        row = index.row()
        current_value = self.array[row][column]
        try:
            self.array[row][ column] = current_value.__class__(value)
        except ValueError as e:
            print(e)
            QMessageBox.critical(self.parent(), "Error",
                                 "Value error: %s" % str(e))
            return False
        return True

    def rowCount(self, index=QModelIndex()):
        """DataFrame row number"""
        return self.total_rows

    def columnCount(self, index=QModelIndex()):
        """DataFrame column number"""
        # This is done to implement series
        return self.total_cols


class TableEditor(QDialog):
    """ Data Frame Editor Dialog """

    def __init__(self, data, parent=None):
        super(TableEditor, self).__init__(parent)
        # Destroying the C++ object right after closing the dialog box,
        # otherwise it may be garbage-collected in another QThread
        # (e.g. the editor's analysis thread in Spyder), thus leading to
        # a segmentation fault on UNIX or an application crash on Windows
        dataModel = TableModel(data)
        dataTableView = QTableView()
        dataTableView.setModel(dataModel)
        self.setMinimumSize(400, 300)
        vbox = QVBoxLayout()
        vbox.addWidget(dataTableView)
        # Make the dialog act as a window
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setLayout(vbox)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TransPy")
    form = TableEditor(link_table)
    form.show()
    app.exec_()


main()