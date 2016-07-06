# -*- coding: utf-8 -*-
#
# Copyright © 2009- Spyder development team
# Licensed under the terms of the New BSD License
#
# DataFrameModel is based on the class ArrayModel from array editor
# and the class DataFrameModel from the pandas project.
# Present in pandas.sandbox.qtpandas in v0.13.1
# Copyright (c) 2011-2012, Lambda Foundry, Inc.
# and PyData Development Team All rights reserved

"""
Pandas DataFrame Editor Dialog
"""

# Third party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import transpy as tp


class TableModel(QAbstractTableModel):
    """ DataFrame Table Model"""
    def __init__(self, structured_array, format="%.3g",parent=None):
        super(TableModel,self).__init__(parent)
        self.array = structured_array
        try:
            self.tb_header = structured_array.dtype.names
        except AttributeError:
            self.tb_header = self.array._col_idx
        if self.tb_header is None:
            self.tb_header = self.array._col_idx

        self._format = format
        
        self.total_rows = self.array.shape[0]
        try:
            self.total_cols = self.array.dtype.names.__len__()
        except AttributeError:
            self.total_cols = self.array.shape[1]   # for Matrix

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
            return str(self.tb_header[section])
        if orientation == Qt.Vertical:
            if isinstance(self.array, tp.Matrix):
                return str(self.array._row_idx[section])
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
            self.array[row][column] = current_value.__class__(value)
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


class TableEditor(QDockWidget):
    """ Data Frame Editor Dialog """
    def __init__(self, data, title, parent=None):
        super(TableEditor, self).__init__(title, parent)
        # Destroying the C++ object right after closing the dialog box,
        # otherwise it may be garbage-collected in another QThread
        # (e.g. the editor's analysis thread in Spyder), thus leading to
        # a segmentation fault on UNIX or an application crash on Windows
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.dataModel = TableModel(data)
        self.dataTableView = QTableView()
        self.dataTableView.setModel(self.dataModel)

        btn_layout = QHBoxLayout()
        # btn_layout.addStretch()
        # format_btn = QPushButton("Format")
        # disable format button for int type
        # btn_layout.addWidget(format_btn)
        # format_btn.clicked.connect(self.change_format)
        # resize_btn = QPushButton('Resize')
        # btn_layout.addWidget(resize_btn)
        # resize_btn.clicked.connect(self.resize_to_contents)

        vbox = QVBoxLayout()
        vbox.addWidget(self.dataTableView)
        vbox.addLayout(btn_layout)
        in_widget = QWidget()
        in_widget.setLayout(vbox)
        self.setWidget(in_widget)

    def change_format(self):
        """Change display format"""
        format, valid = QInputDialog.getText(self, 'Format',
                                             "Float formatting",
                                             QLineEdit.Normal,
                                             self.dataModel.get_format())
        if valid:
            format = str(format)
            try:
                format % 1.1
            except:
                QMessageBox.critical(self, "Error",
                                     "Format (%s) is incorrect" % format)
                return
            self.dataModel.set_format(format)

    def resize_to_contents(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.dataTable.resizeColumnsToContents()
        QApplication.restoreOverrideCursor()

