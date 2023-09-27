# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_collect_ww_data.ui'
##
## Created by: Qt User Interface Compiler version 6.1.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(498, 556)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.SelectWWLabel = QLabel(self.centralwidget)
        self.SelectWWLabel.setObjectName(u"SelectWWLabel")

        self.verticalLayout.addWidget(self.SelectWWLabel)

        self.SelectDistributionComboBox = QComboBox(self.centralwidget)
        self.SelectDistributionComboBox.setObjectName(u"SelectDistributionComboBox")

        self.verticalLayout.addWidget(self.SelectDistributionComboBox)

        self.CheckboxesHorizontalLayout = QHBoxLayout()
        self.CheckboxesHorizontalLayout.setObjectName(u"CheckboxesHorizontalLayout")
        self.AddToExistsCheckBox = QCheckBox(self.centralwidget)
        self.AddToExistsCheckBox.setObjectName(u"AddToExistsCheckBox")

        self.CheckboxesHorizontalLayout.addWidget(self.AddToExistsCheckBox)

        self.LogScaleCheckBox = QCheckBox(self.centralwidget)
        self.LogScaleCheckBox.setObjectName(u"LogScaleCheckBox")

        self.CheckboxesHorizontalLayout.addWidget(self.LogScaleCheckBox)


        self.verticalLayout.addLayout(self.CheckboxesHorizontalLayout)

        self.treeView = QTreeView(self.centralwidget)
        self.treeView.setObjectName(u"treeView")

        self.verticalLayout.addWidget(self.treeView)

        self.LowPadHorizontalLayout = QHBoxLayout()
        self.LowPadHorizontalLayout.setObjectName(u"LowPadHorizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.LowPadHorizontalLayout.addItem(self.horizontalSpacer)

        self.ExtractButton = QPushButton(self.centralwidget)
        self.ExtractButton.setObjectName(u"ExtractButton")

        self.LowPadHorizontalLayout.addWidget(self.ExtractButton)

        self.PlotButton = QPushButton(self.centralwidget)
        self.PlotButton.setObjectName(u"PlotButton")

        self.LowPadHorizontalLayout.addWidget(self.PlotButton)


        self.verticalLayout.addLayout(self.LowPadHorizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 498, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Distributions Collector", None))
        self.SelectWWLabel.setText(QCoreApplication.translate("MainWindow", u"Select distribution", None))
        self.AddToExistsCheckBox.setText(QCoreApplication.translate("MainWindow", u"Add data to exists plot", None))
        self.LogScaleCheckBox.setText(QCoreApplication.translate("MainWindow", u"Log scale", None))
        self.ExtractButton.setText(QCoreApplication.translate("MainWindow", u"Extract", None))
        self.PlotButton.setText(QCoreApplication.translate("MainWindow", u"Plot", None))
    # retranslateUi

