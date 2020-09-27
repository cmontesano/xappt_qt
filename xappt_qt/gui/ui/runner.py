# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'runner.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_RunDialog(object):
    def setupUi(self, RunDialog):
        if not RunDialog.objectName():
            RunDialog.setObjectName(u"RunDialog")
        RunDialog.resize(700, 400)
        self.gridLayout_2 = QGridLayout(RunDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btnOk = QPushButton(RunDialog)
        self.btnOk.setObjectName(u"btnOk")

        self.horizontalLayout.addWidget(self.btnOk)

        self.btnClose = QPushButton(RunDialog)
        self.btnClose.setObjectName(u"btnClose")

        self.horizontalLayout.addWidget(self.btnClose)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)

        self.placeholder = QLabel(RunDialog)
        self.placeholder.setObjectName(u"placeholder")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.placeholder.sizePolicy().hasHeightForWidth())
        self.placeholder.setSizePolicy(sizePolicy)
        self.placeholder.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.placeholder, 0, 0, 1, 1)

        self.progressBar = QProgressBar(RunDialog)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 1, 0, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.retranslateUi(RunDialog)

        QMetaObject.connectSlotsByName(RunDialog)
    # setupUi

    def retranslateUi(self, RunDialog):
        RunDialog.setWindowTitle(QCoreApplication.translate("RunDialog", u"Dialog", None))
        self.btnOk.setText(QCoreApplication.translate("RunDialog", u"Run", None))
        self.btnClose.setText(QCoreApplication.translate("RunDialog", u"Close", None))
        self.placeholder.setText(QCoreApplication.translate("RunDialog", u"placeholder", None))
        self.progressBar.setFormat("")
    # retranslateUi

