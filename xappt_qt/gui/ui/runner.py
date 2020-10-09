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
        RunDialog.resize(753, 645)
        self.gridLayout_2 = QGridLayout(RunDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.splitter = QSplitter(RunDialog)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(12)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.widget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 731, 186))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.placeholder = QLabel(self.scrollAreaWidgetContents)
        self.placeholder.setObjectName(u"placeholder")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.placeholder.sizePolicy().hasHeightForWidth())
        self.placeholder.setSizePolicy(sizePolicy)
        self.placeholder.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.placeholder, 0, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.progressBar = QProgressBar(self.widget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.verticalLayout_2.addWidget(self.progressBar)

        self.splitter.addWidget(self.widget)
        self.txtOutput = QTextEdit(self.splitter)
        self.txtOutput.setObjectName(u"txtOutput")
        self.txtOutput.setTabChangesFocus(True)
        self.txtOutput.setUndoRedoEnabled(False)
        self.txtOutput.setLineWrapMode(QTextEdit.NoWrap)
        self.txtOutput.setReadOnly(True)
        self.txtOutput.setTabStopWidth(40)
        self.splitter.addWidget(self.txtOutput)

        self.gridLayout_2.addWidget(self.splitter, 0, 0, 1, 1)

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


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.retranslateUi(RunDialog)

        QMetaObject.connectSlotsByName(RunDialog)
    # setupUi

    def retranslateUi(self, RunDialog):
        RunDialog.setWindowTitle(QCoreApplication.translate("RunDialog", u"Dialog", None))
        self.placeholder.setText(QCoreApplication.translate("RunDialog", u"placeholder", None))
        self.progressBar.setFormat("")
        self.txtOutput.setHtml(QCoreApplication.translate("RunDialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;\" bgcolor=\"#000000\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.btnOk.setText(QCoreApplication.translate("RunDialog", u"Run", None))
        self.btnClose.setText(QCoreApplication.translate("RunDialog", u"Close", None))
    # retranslateUi

