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
        Browser.resize(484, 473)
        self.centralwidget = QWidget(Browser)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.treeTools = QTreeWidget(self.centralwidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.treeTools.setHeaderItem(__qtreewidgetitem)
        self.treeTools.setObjectName(u"treeTools")
        self.treeTools.setAlternatingRowColors(True)
        self.treeTools.setRootIsDecorated(False)
        self.treeTools.setSortingEnabled(True)
        self.treeTools.header().setVisible(False)

        self.gridLayout.addWidget(self.treeTools, 0, 0, 1, 2)

        self.labelHelp = QLabel(self.centralwidget)
        self.labelHelp.setObjectName(u"labelHelp")
        self.labelHelp.setWordWrap(True)

        self.gridLayout.addWidget(self.labelHelp, 1, 0, 1, 2)

        Browser.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Browser)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 484, 27))
        Browser.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Browser)
        self.statusbar.setObjectName(u"statusbar")
        Browser.setStatusBar(self.statusbar)

        self.retranslateUi(Browser)

        QMetaObject.connectSlotsByName(Browser)
    # setupUi

    def retranslateUi(self, Browser):
        Browser.setWindowTitle(QCoreApplication.translate("Browser", u"Xappt Browser", None))
        self.labelHelp.setText("")
    # retranslateUi

