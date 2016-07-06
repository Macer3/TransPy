# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'assignment.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!
import sys
from transpy import IDTable, Net, Matrix, IDGroupTable
from transpy.compute.assignment import *
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(380, 420)
        self.gridLayout_4 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.fileGroup = QtWidgets.QGroupBox(Dialog)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.fileGroup.setFont(font)
        self.fileGroup.setObjectName("fileGroup")
        self.gridLayout_1 = QtWidgets.QGridLayout(self.fileGroup)
        self.gridLayout_1.setObjectName("gridLayout_1")
        self.label = QtWidgets.QLabel(self.fileGroup)

        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_1.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.fileGroup)

        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_1.addWidget(self.label_3, 1, 0, 1, 1)
        self.nameEdit = QtWidgets.QLineEdit(self.fileGroup)

        self.nameEdit.setFont(font)
        self.nameEdit.setText("")
        self.nameEdit.setObjectName("nameEdit")
        self.gridLayout_1.addWidget(self.nameEdit, 1, 3, 1, 1)
        self.netBox = QtWidgets.QComboBox(self.fileGroup)

        self.netBox.setFont(font)
        self.netBox.setEditable(True)
        self.netBox.setObjectName("netBox")
        self.netBox.addItem("")
        self.gridLayout_1.addWidget(self.netBox, 0, 3, 1, 1)
        self.linkBox = QtWidgets.QComboBox(self.fileGroup)

        self.linkBox.setFont(font)
        self.linkBox.setEditable(True)
        self.linkBox.setObjectName("linkBox")
        self.linkBox.addItem("")
        self.gridLayout_1.addWidget(self.linkBox, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.fileGroup)

        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_1.addWidget(self.label_2, 0, 2, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.fileGroup)

        self.label_23.setFont(font)
        self.label_23.setAlignment(QtCore.Qt.AlignCenter)
        self.label_23.setObjectName("label_23")
        self.gridLayout_1.addWidget(self.label_23, 1, 2, 1, 1)
        self.ODBox = QtWidgets.QComboBox(self.fileGroup)

        self.ODBox.setFont(font)
        self.ODBox.setEditable(True)
        self.ODBox.setObjectName("ODBox")
        self.ODBox.addItem("")
        self.gridLayout_1.addWidget(self.ODBox, 1, 1, 1, 1)
        self.gridLayout_4.addWidget(self.fileGroup, 0, 0, 1, 2)
        self.globalGroup = QtWidgets.QGroupBox(Dialog)

        self.globalGroup.setFont(font)
        self.globalGroup.setObjectName("globalGroup")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.globalGroup)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_16 = QtWidgets.QLabel(self.globalGroup)

        self.label_16.setFont(font)
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setObjectName("label_16")
        self.gridLayout_3.addWidget(self.label_16, 0, 0, 1, 1)
        self.alphaEdit = QtWidgets.QLineEdit(self.globalGroup)

        self.alphaEdit.setFont(font)
        self.alphaEdit.setObjectName("alphaEdit")
        self.gridLayout_3.addWidget(self.alphaEdit, 0, 1, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.globalGroup)

        self.label_17.setFont(font)
        self.label_17.setAlignment(QtCore.Qt.AlignCenter)
        self.label_17.setObjectName("label_17")
        self.gridLayout_3.addWidget(self.label_17, 0, 2, 1, 1)
        self.betaEdit = QtWidgets.QLineEdit(self.globalGroup)

        self.betaEdit.setFont(font)
        self.betaEdit.setObjectName("betaEdit")
        self.gridLayout_3.addWidget(self.betaEdit, 0, 3, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.globalGroup)

        self.label_18.setFont(font)
        self.label_18.setAlignment(QtCore.Qt.AlignCenter)
        self.label_18.setObjectName("label_18")
        self.gridLayout_3.addWidget(self.label_18, 1, 0, 1, 1)
        self.convergenceEdit = QtWidgets.QLineEdit(self.globalGroup)

        self.convergenceEdit.setFont(font)
        self.convergenceEdit.setObjectName("convergenceEdit")
        self.gridLayout_3.addWidget(self.convergenceEdit, 1, 1, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.globalGroup)

        self.label_19.setFont(font)
        self.label_19.setAlignment(QtCore.Qt.AlignCenter)
        self.label_19.setObjectName("label_19")
        self.gridLayout_3.addWidget(self.label_19, 1, 2, 1, 1)
        self.maxIterEdit = QtWidgets.QLineEdit(self.globalGroup)

        self.maxIterEdit.setFont(font)
        self.maxIterEdit.setObjectName("maxIterEdit")
        self.gridLayout_3.addWidget(self.maxIterEdit, 1, 3, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.globalGroup)

        self.label_20.setFont(font)
        self.label_20.setAlignment(QtCore.Qt.AlignCenter)
        self.label_20.setObjectName("label_20")
        self.gridLayout_3.addWidget(self.label_20, 2, 0, 1, 1)
        self.typeFieldBox = QtWidgets.QComboBox(self.globalGroup)

        self.typeFieldBox.setFont(font)
        self.typeFieldBox.setEditable(True)
        self.typeFieldBox.setObjectName("typeFieldBox")
        self.typeFieldBox.addItem("")
        self.gridLayout_3.addWidget(self.typeFieldBox, 2, 1, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.globalGroup)

        self.label_21.setFont(font)
        self.label_21.setAlignment(QtCore.Qt.AlignCenter)
        self.label_21.setObjectName("label_21")
        self.gridLayout_3.addWidget(self.label_21, 2, 2, 1, 1)
        self.typeDictBox = QtWidgets.QComboBox(self.globalGroup)

        self.typeDictBox.setFont(font)
        self.typeDictBox.setEditable(True)
        self.typeDictBox.setObjectName("typeDictBox")
        self.typeDictBox.addItem("")
        self.gridLayout_3.addWidget(self.typeDictBox, 2, 3, 1, 1)
        self.gridLayout_4.addWidget(self.globalGroup, 2, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(176, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 3, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)

        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_4.addWidget(self.buttonBox, 3, 1, 1, 1)
        self.paramGroup = QtWidgets.QGroupBox(Dialog)

        self.paramGroup.setFont(font)
        self.paramGroup.setObjectName("paramGroup")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.paramGroup)
        self.gridLayout_2.setContentsMargins(9, 9, -1, -1)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.delayBox = QtWidgets.QComboBox(self.paramGroup)

        self.delayBox.setFont(font)
        self.delayBox.setEditable(True)
        self.delayBox.setObjectName("delayBox")
        self.delayBox.addItem("")
        self.delayBox.addItem("")
        self.delayBox.addItem("")
        self.gridLayout_2.addWidget(self.delayBox, 3, 1, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.paramGroup)

        self.label_22.setFont(font)
        self.label_22.setAlignment(QtCore.Qt.AlignCenter)
        self.label_22.setObjectName("label_22")
        self.gridLayout_2.addWidget(self.label_22, 3, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.paramGroup)

        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)
        self.timeBox = QtWidgets.QComboBox(self.paramGroup)

        self.timeBox.setFont(font)
        self.timeBox.setEditable(True)
        self.timeBox.setObjectName("timeBox")
        self.timeBox.addItem("")
        self.gridLayout_2.addWidget(self.timeBox, 1, 1, 1, 1)
        self.focusEdit = QtWidgets.QLineEdit(self.paramGroup)

        self.focusEdit.setFont(font)
        self.focusEdit.setText("")
        self.focusEdit.setObjectName("focusEdit")
        self.gridLayout_2.addWidget(self.focusEdit, 3, 3, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.paramGroup)

        self.label_13.setFont(font)
        self.label_13.setAlignment(QtCore.Qt.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 2, 0, 1, 1)
        self.methodBox = QtWidgets.QComboBox(self.paramGroup)

        self.methodBox.setFont(font)
        self.methodBox.setEditable(True)
        self.methodBox.setObjectName("methodBox")
        self.methodBox.addItem("")
        self.methodBox.addItem("")
        self.gridLayout_2.addWidget(self.methodBox, 0, 1, 1, 1)
        self.betaBox = QtWidgets.QComboBox(self.paramGroup)

        self.betaBox.setFont(font)
        self.betaBox.setEditable(True)
        self.betaBox.setObjectName("betaBox")
        self.betaBox.addItem("")
        self.gridLayout_2.addWidget(self.betaBox, 2, 3, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.paramGroup)

        self.label_15.setFont(font)
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 0, 2, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.paramGroup)

        self.label_11.setFont(font)
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 1, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.paramGroup)

        self.label_12.setFont(font)
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 1, 2, 1, 1)
        self.alphaBox = QtWidgets.QComboBox(self.paramGroup)

        self.alphaBox.setFont(font)
        self.alphaBox.setEditable(True)
        self.alphaBox.setObjectName("alphaBox")
        self.alphaBox.addItem("")
        self.gridLayout_2.addWidget(self.alphaBox, 2, 1, 1, 1)
        self.label_25 = QtWidgets.QLabel(self.paramGroup)

        self.label_25.setFont(font)
        self.label_25.setAlignment(QtCore.Qt.AlignCenter)
        self.label_25.setObjectName("label_25")
        self.gridLayout_2.addWidget(self.label_25, 3, 2, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.paramGroup)

        self.label_14.setFont(font)
        self.label_14.setAlignment(QtCore.Qt.AlignCenter)
        self.label_14.setObjectName("label_14")
        self.gridLayout_2.addWidget(self.label_14, 2, 2, 1, 1)
        self.preloadBox = QtWidgets.QComboBox(self.paramGroup)

        self.preloadBox.setFont(font)
        self.preloadBox.setEditable(True)
        self.preloadBox.setObjectName("preloadBox")
        self.preloadBox.addItem("")
        self.gridLayout_2.addWidget(self.preloadBox, 0, 3, 1, 1)
        self.capacityBox = QtWidgets.QComboBox(self.paramGroup)

        self.capacityBox.setFont(font)
        self.capacityBox.setEditable(True)
        self.capacityBox.setObjectName("capacityBox")
        self.capacityBox.addItem("")
        self.gridLayout_2.addWidget(self.capacityBox, 1, 3, 1, 1)
        self.gridLayout_4.addWidget(self.paramGroup, 1, 0, 1, 2)
        self.label.setBuddy(self.linkBox)
        self.label_3.setBuddy(self.ODBox)
        self.label_2.setBuddy(self.netBox)
        self.label_23.setBuddy(self.nameEdit)
        self.label_16.setBuddy(self.alphaEdit)
        self.label_17.setBuddy(self.betaEdit)
        self.label_18.setBuddy(self.convergenceEdit)
        self.label_19.setBuddy(self.maxIterEdit)
        self.label_20.setBuddy(self.typeFieldBox)
        self.label_21.setBuddy(self.typeDictBox)
        self.label_22.setBuddy(self.delayBox)
        self.label_4.setBuddy(self.methodBox)
        self.label_13.setBuddy(self.alphaBox)
        self.label_15.setBuddy(self.preloadBox)
        self.label_11.setBuddy(self.timeBox)
        self.label_12.setBuddy(self.capacityBox)
        self.label_25.setBuddy(self.focusEdit)
        self.label_14.setBuddy(self.betaBox)

        self.retranslateUi(Dialog)
        self.methodBox.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.linkBox, self.netBox)
        Dialog.setTabOrder(self.netBox, self.ODBox)
        Dialog.setTabOrder(self.ODBox, self.nameEdit)
        Dialog.setTabOrder(self.nameEdit, self.methodBox)
        Dialog.setTabOrder(self.methodBox, self.preloadBox)
        Dialog.setTabOrder(self.preloadBox, self.timeBox)
        Dialog.setTabOrder(self.timeBox, self.capacityBox)
        Dialog.setTabOrder(self.capacityBox, self.alphaBox)
        Dialog.setTabOrder(self.alphaBox, self.betaBox)
        Dialog.setTabOrder(self.betaBox, self.delayBox)
        Dialog.setTabOrder(self.delayBox, self.focusEdit)
        Dialog.setTabOrder(self.focusEdit, self.alphaEdit)
        Dialog.setTabOrder(self.alphaEdit, self.betaEdit)
        Dialog.setTabOrder(self.betaEdit, self.convergenceEdit)
        Dialog.setTabOrder(self.convergenceEdit, self.maxIterEdit)
        Dialog.setTabOrder(self.maxIterEdit, self.typeFieldBox)
        Dialog.setTabOrder(self.typeFieldBox, self.typeDictBox)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "交通分配"))
        self.fileGroup.setTitle(_translate("Dialog", "文件"))
        self.label.setText(_translate("Dialog", "路段表"))
        self.label_3.setText(_translate("Dialog", "OD矩阵"))
        self.label_2.setText(_translate("Dialog", "网络文件"))
        self.label_23.setText(_translate("Dialog", "输出名称"))
        self.globalGroup.setTitle(_translate("Dialog", "全局参数设置"))
        self.label_16.setText(_translate("Dialog", "alpha"))
        self.alphaEdit.setText(_translate("Dialog", "0.15"))
        self.label_17.setText(_translate("Dialog", "beta"))
        self.betaEdit.setText(_translate("Dialog", "4"))
        self.label_18.setText(_translate("Dialog", "收敛误差"))
        self.convergenceEdit.setText(_translate("Dialog", "0.001"))
        self.label_19.setText(_translate("Dialog", "最大迭代次数"))
        self.maxIterEdit.setText(_translate("Dialog", "100"))
        self.label_20.setText(_translate("Dialog", "路段类型域"))
        self.label_21.setText(_translate("Dialog", "类型字典"))
        self.paramGroup.setTitle(_translate("Dialog", "参数设置"))
        self.delayBox.setItemText(0, _translate("Dialog", "all"))
        self.delayBox.setItemText(1, _translate("Dialog", "ban"))
        self.delayBox.setItemText(2, _translate("Dialog", "none"))
        self.label_22.setText(_translate("Dialog", "延误"))
        self.label_4.setText(_translate("Dialog", "方式"))
        self.label_13.setText(_translate("Dialog", "alpha"))
        self.methodBox.setItemText(0, _translate("Dialog", "AON"))
        self.methodBox.setItemText(1, _translate("Dialog", "UE"))
        self.label_15.setText(_translate("Dialog", "预分配"))
        self.label_11.setText(_translate("Dialog", "时间"))
        self.label_12.setText(_translate("Dialog", "通行能力"))
        self.label_25.setText(_translate("Dialog", "兴趣节点"))
        self.label_14.setText(_translate("Dialog", "beta"))


class assign_dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(assign_dialog,self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle('交通分配')
        self.disable_box(True)
        self.disabled = True
        self.var_dict = parent.var_dict
        self.var_name_dic = {'IDTable':[],
                             'IDGroupTable':[],
                             'Matrix':[],
                             'Net':[]}

        # 给文件框赋初值
        for key, value in self.var_dict.items():
            if isinstance(value, IDTable):
                self.var_name_dic['IDTable'].append(key)
            elif isinstance(value, IDGroupTable):
                self.var_name_dic['IDTable'].append(key)
            elif isinstance(value, Matrix):
                self.var_name_dic['Matrix'].append(key)
            elif isinstance(value, Net):
                self.var_name_dic['Net'].append(key)
        self.ui.ODBox.addItems(self.var_name_dic['Matrix'])
        self.ui.netBox.addItems(self.var_name_dic['Net'])
        self.ui.linkBox.addItems(self.var_name_dic['IDTable'])
        self.build_signal()

    def build_signal(self):
        self.ui.netBox.currentIndexChanged.connect(self.file_enable)
        self.ui.buttonBox.accepted.connect(self.do_assignment)
        self.ui.buttonBox.rejected.connect(self.reject)

    def file_enable(self):
        """使参数框可行或不可行，"""
        net_name = self.ui.netBox.currentText()
        if net_name is '':
            if self.disabled is False:
                self.ui.timeBox.clear()
                self.ui.capacityBox.clear()
                self.ui.preloadBox.clear()
                self.ui.alphaBox.clear()
                self.ui.betaBox.clear()
                self.ui.typeFieldBox.clear()
                self.disable_box(True)
        else:
            self.disable_box(False)
            net = self.var_dict[self.ui.netBox.currentText()]
            net_fields = list(net.names)
            self.ui.timeBox.addItems(net_fields)
            self.ui.capacityBox.addItems(net_fields)
            self.ui.preloadBox.addItems(net_fields)
            self.ui.alphaBox.addItems(net_fields)
            self.ui.betaBox.addItems(net_fields)
            self.ui.typeFieldBox.addItems(net_fields)


    def disable_box(self, flag):
        self.ui.alphaBox.setDisabled(flag)
        self.ui.preloadBox.setDisabled(flag)
        self.ui.timeBox.setDisabled(flag)
        self.ui.capacityBox.setDisabled(flag)
        self.ui.betaBox.setDisabled(flag)
        self.ui.typeFieldBox.setDisabled(flag)
        self.disabled = flag

    def do_assignment(self):
        cfg = AssignConfig()
        try:
            cfg.method = self.ui.methodBox.currentText()
            cfg.time_field = self.ui.timeBox.currentText()
            cfg.capacity_field = self.ui.capacityBox.currentText()
            cfg.convergence = self.ui.convergenceEdit.text()
            cfg.max_iteration = int(self.ui.maxIterEdit.text())
            cfg.preload_field = self.ui.preloadBox.currentText()
            cfg.turn_delay_type = self.ui.delayBox.currentText()
            cfg.global_alpha = float(self.ui.alphaEdit.text())
            cfg.global_beta = float(self.ui.betaEdit.text())
            cfg.convergence = float(self.ui.convergenceEdit.text())
            cfg.max_iteration = int(self.ui.maxIterEdit.text())
            cfg.print_frequency = 0

            net_name = self.ui.netBox.currentText()
            link_name = self.ui.linkBox.currentText()
            matrix_name = self.ui.ODBox.currentText()
            pre = self.ui.nameEdit.text()
            arcs_flow_name = pre + 'arcs_flow'
            turns_flow_name = pre + 'turns_flow'

            arcs_flow, turns_flow, summary = \
                user_equilibrium(self.var_dict[net_name],
                                 self.var_dict[matrix_name],
                                 self.var_dict[link_name],
                                 cfg)
            self.var_dict[arcs_flow_name] = arcs_flow
            self.var_dict[turns_flow_name] = turns_flow
        except BaseException as e:
            QtWidgets.QMessageBox.warning(
                self, 'Error',"输入参数有错，请检查后重试。 %s" % str(e))
            return False

        QtWidgets.QMessageBox.information(self,'Success', '分配成功！')
        self.done(1)





# app = QtWidgets.QApplication(sys.argv)
# myapp = assign_dialog()
# myapp.show()
# sys.exit(app.exec_())