# -*- coding: utf-8 -*-


#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ToolInterface(object):
    def setupUi(self, ToolInterface):
        ToolInterface.setObjectName("ToolInterface")
        ToolInterface.resize(876, 624)
        self.gridLayout = QtWidgets.QGridLayout(ToolInterface)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(ToolInterface)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.toolContainer = QtWidgets.QWidget(self.splitter)
        self.toolContainer.setObjectName("toolContainer")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.toolContainer)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.consoleContainer = QtWidgets.QWidget(self.splitter)
        self.consoleContainer.setObjectName("consoleContainer")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.consoleContainer)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(ToolInterface)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setFormat("")
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnRun = QtWidgets.QPushButton(ToolInterface)
        self.btnRun.setObjectName("btnRun")
        self.horizontalLayout.addWidget(self.btnRun)
        self.btnAdvance = QtWidgets.QPushButton(ToolInterface)
        self.btnAdvance.setObjectName("btnAdvance")
        self.horizontalLayout.addWidget(self.btnAdvance)
        self.btnRunAndAdvance = QtWidgets.QPushButton(ToolInterface)
        self.btnRunAndAdvance.setObjectName("btnRunAndAdvance")
        self.horizontalLayout.addWidget(self.btnRunAndAdvance)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.retranslateUi(ToolInterface)
        QtCore.QMetaObject.connectSlotsByName(ToolInterface)

    def retranslateUi(self, ToolInterface):
        _translate = QtCore.QCoreApplication.translate
        ToolInterface.setWindowTitle(_translate("ToolInterface", "Dialog"))
        self.btnRun.setText(_translate("ToolInterface", "Run"))
        self.btnAdvance.setText(_translate("ToolInterface", "Next"))
        self.btnRunAndAdvance.setText(_translate("ToolInterface", "Next"))
