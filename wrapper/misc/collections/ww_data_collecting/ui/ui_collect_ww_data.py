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
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.CollectWWDataTab = QWidget()
        self.CollectWWDataTab.setObjectName(u"CollectWWDataTab")
        self.verticalLayout_3 = QVBoxLayout(self.CollectWWDataTab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.CollectMainVerticalLayout = QVBoxLayout()
        self.CollectMainVerticalLayout.setObjectName(u"CollectMainVerticalLayout")
        self.SelectWWLabel = QLabel(self.CollectWWDataTab)
        self.SelectWWLabel.setObjectName(u"SelectWWLabel")

        self.CollectMainVerticalLayout.addWidget(self.SelectWWLabel)

        self.SelectWWHorizontalLayout = QHBoxLayout()
        self.SelectWWHorizontalLayout.setObjectName(u"SelectWWHorizontalLayout")
        self.spinBox = QSpinBox(self.CollectWWDataTab)
        self.spinBox.setObjectName(u"spinBox")

        self.SelectWWHorizontalLayout.addWidget(self.spinBox)

        self.SelectWWHorizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.SelectWWHorizontalLayout.addItem(self.SelectWWHorizontalSpacer)


        self.CollectMainVerticalLayout.addLayout(self.SelectWWHorizontalLayout)

        self.AddToExistsCheckBox = QCheckBox(self.CollectWWDataTab)
        self.AddToExistsCheckBox.setObjectName(u"AddToExistsCheckBox")

        self.CollectMainVerticalLayout.addWidget(self.AddToExistsCheckBox)

        self.treeWidget = QTreeWidget(self.CollectWWDataTab)
        self.treeWidget.setObjectName(u"treeWidget")

        self.CollectMainVerticalLayout.addWidget(self.treeWidget)

        self.LowPadHorizontalLayout = QHBoxLayout()
        self.LowPadHorizontalLayout.setObjectName(u"LowPadHorizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.LowPadHorizontalLayout.addItem(self.horizontalSpacer)

        self.pushButton_2 = QPushButton(self.CollectWWDataTab)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.LowPadHorizontalLayout.addWidget(self.pushButton_2)

        self.pushButton = QPushButton(self.CollectWWDataTab)
        self.pushButton.setObjectName(u"pushButton")

        self.LowPadHorizontalLayout.addWidget(self.pushButton)


        self.CollectMainVerticalLayout.addLayout(self.LowPadHorizontalLayout)


        self.verticalLayout_3.addLayout(self.CollectMainVerticalLayout)

        self.tabWidget.addTab(self.CollectWWDataTab, "")
        self.ExtractWWDataTab = QWidget()
        self.ExtractWWDataTab.setObjectName(u"ExtractWWDataTab")
        self.verticalLayoutWidget_2 = QWidget(self.ExtractWWDataTab)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(0, 10, 481, 451))
        self.ExtractWWVerticalLayout = QVBoxLayout(self.verticalLayoutWidget_2)
        self.ExtractWWVerticalLayout.setObjectName(u"ExtractWWVerticalLayout")
        self.ExtractWWVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget.addTab(self.ExtractWWDataTab, "")
        self.ViewWWTab = QWidget()
        self.ViewWWTab.setObjectName(u"ViewWWTab")
        self.tabWidget.addTab(self.ViewWWTab, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 498, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.SelectWWLabel.setText(QCoreApplication.translate("MainWindow", u"Select ww number", None))
        self.AddToExistsCheckBox.setText(QCoreApplication.translate("MainWindow", u"Add data to exists plot", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("MainWindow", u"Size", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("MainWindow", u"Type", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"Date Modified", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Name", None));
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.CollectWWDataTab), QCoreApplication.translate("MainWindow", u"Collect", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ExtractWWDataTab), QCoreApplication.translate("MainWindow", u"Extract", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ViewWWTab), QCoreApplication.translate("MainWindow", u"WW descriptions view", None))
    # retranslateUi

