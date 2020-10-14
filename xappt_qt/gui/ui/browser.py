# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'browser.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Browser(object):
    def setupUi(self, Browser):
        Browser.setObjectName("Browser")
        Browser.resize(605, 643)
        self.centralwidget = QtWidgets.QWidget(Browser)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setObjectName("tabWidget")
        self.tabTools = QtWidgets.QWidget()
        self.tabTools.setObjectName("tabTools")
        self.gridLayout = QtWidgets.QGridLayout(self.tabTools)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.txtSearch = QtWidgets.QLineEdit(self.tabTools)
        self.txtSearch.setObjectName("txtSearch")
        self.horizontalLayout.addWidget(self.txtSearch)
        self.btnClear = QtWidgets.QToolButton(self.tabTools)
        self.btnClear.setObjectName("btnClear")
        self.horizontalLayout.addWidget(self.btnClear)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.treeTools = QtWidgets.QTreeWidget(self.tabTools)
        self.treeTools.setAlternatingRowColors(True)
        self.treeTools.setRootIsDecorated(True)
        self.treeTools.setObjectName("treeTools")
        self.treeTools.headerItem().setText(0, "1")
        self.treeTools.header().setVisible(False)
        self.gridLayout.addWidget(self.treeTools, 1, 0, 1, 1)
        self.labelHelp = QtWidgets.QLabel(self.tabTools)
        self.labelHelp.setText("")
        self.labelHelp.setWordWrap(True)
        self.labelHelp.setObjectName("labelHelp")
        self.gridLayout.addWidget(self.labelHelp, 2, 0, 1, 1)
        self.tabWidget.addTab(self.tabTools, "")
        self.tabOptions = QtWidgets.QWidget()
        self.tabOptions.setObjectName("tabOptions")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tabOptions)
        self.gridLayout_4.setObjectName("gridLayout_4")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem, 1, 0, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setSpacing(12)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.chkLaunchNewProcess = QtWidgets.QCheckBox(self.tabOptions)
        self.chkLaunchNewProcess.setObjectName("chkLaunchNewProcess")
        self.gridLayout_3.addWidget(self.chkLaunchNewProcess, 0, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabOptions, "")
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        Browser.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Browser)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 605, 27))
        self.menubar.setObjectName("menubar")
        Browser.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Browser)
        self.statusbar.setObjectName("statusbar")
        Browser.setStatusBar(self.statusbar)

        self.retranslateUi(Browser)
        self.tabWidget.setCurrentIndex(0)
        self.btnClear.clicked.connect(self.txtSearch.clear)
        QtCore.QMetaObject.connectSlotsByName(Browser)
        Browser.setTabOrder(self.txtSearch, self.btnClear)
        Browser.setTabOrder(self.btnClear, self.treeTools)

    def retranslateUi(self, Browser):
        _translate = QtCore.QCoreApplication.translate
        Browser.setWindowTitle(_translate("Browser", "Xappt Browser"))
        self.txtSearch.setPlaceholderText(_translate("Browser", "Search"))
        self.btnClear.setText(_translate("Browser", "⌫"))
        self.treeTools.setSortingEnabled(False)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTools), _translate("Browser", "Tools"))
        self.chkLaunchNewProcess.setText(_translate("Browser", "Launch tools in new process"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabOptions), _translate("Browser", "Options"))
