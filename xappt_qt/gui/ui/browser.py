# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'browser.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Browser(object):
    def setupUi(self, Browser):
        if not Browser.objectName():
            Browser.setObjectName(u"Browser")
        Browser.resize(553, 709)
        self.centralwidget = QWidget(Browser)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.labelHelp = QLabel(self.centralwidget)
        self.labelHelp.setObjectName(u"labelHelp")
        self.labelHelp.setWordWrap(True)

        self.gridLayout.addWidget(self.labelHelp, 3, 0, 1, 1)

        self.treeTools = QTreeWidget(self.centralwidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.treeTools.setHeaderItem(__qtreewidgetitem)
        self.treeTools.setObjectName(u"treeTools")
        self.treeTools.setAlternatingRowColors(True)
        self.treeTools.setRootIsDecorated(True)
        self.treeTools.setSortingEnabled(False)
        self.treeTools.header().setVisible(False)

        self.gridLayout.addWidget(self.treeTools, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.txtSearch = QLineEdit(self.centralwidget)
        self.txtSearch.setObjectName(u"txtSearch")

        self.horizontalLayout.addWidget(self.txtSearch)

        self.btnClear = QToolButton(self.centralwidget)
        self.btnClear.setObjectName(u"btnClear")

        self.horizontalLayout.addWidget(self.btnClear)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        Browser.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Browser)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 553, 27))
        Browser.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Browser)
        self.statusbar.setObjectName(u"statusbar")
        Browser.setStatusBar(self.statusbar)
        QWidget.setTabOrder(self.txtSearch, self.btnClear)
        QWidget.setTabOrder(self.btnClear, self.treeTools)

        self.retranslateUi(Browser)
        self.btnClear.clicked.connect(self.txtSearch.clear)

        QMetaObject.connectSlotsByName(Browser)
    # setupUi

    def retranslateUi(self, Browser):
        Browser.setWindowTitle(QCoreApplication.translate("Browser", u"Xappt Browser", None))
        self.labelHelp.setText("")
        self.txtSearch.setPlaceholderText(QCoreApplication.translate("Browser", u"Search", None))
        self.btnClear.setText(QCoreApplication.translate("Browser", u"\u232b", None))
    # retranslateUi

