# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'browser_tab_about.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_tabAbout(object):
    def setupUi(self, tabAbout):
        tabAbout.setObjectName("tabAbout")
        tabAbout.resize(185, 318)
        self.gridLayout = QtWidgets.QGridLayout(tabAbout)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblTitle = QtWidgets.QLabel(tabAbout)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.lblTitle.setFont(font)
        self.lblTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTitle.setObjectName("lblTitle")
        self.verticalLayout.addWidget(self.lblTitle)
        self.txtAbout = QtWidgets.QTextBrowser(tabAbout)
        self.txtAbout.setReadOnly(True)
        self.txtAbout.setOpenExternalLinks(True)
        self.txtAbout.setObjectName("txtAbout")
        self.verticalLayout.addWidget(self.txtAbout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(tabAbout)
        QtCore.QMetaObject.connectSlotsByName(tabAbout)

    def retranslateUi(self, tabAbout):
        _translate = QtCore.QCoreApplication.translate
        tabAbout.setWindowTitle(_translate("tabAbout", "About"))
        self.lblTitle.setText(_translate("tabAbout", "Xappt QT"))
