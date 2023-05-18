# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\projects\python\EDV\ui_files\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setWindowTitle("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setGeometry(QtCore.QRect(0, 40, 151, 511))
        self.treeView.setObjectName("treeView")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(0, 10, 151, 31))
        self.textEdit.setObjectName("textEdit")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(160, 10, 631, 561))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.overview_tab = QtWidgets.QWidget()
        self.overview_tab.setObjectName("overview_tab")
        self.overview_textbrower = QtWidgets.QTextBrowser(self.overview_tab)
        self.overview_textbrower.setGeometry(QtCore.QRect(0, 0, 631, 521))
        self.overview_textbrower.setObjectName("overview_textbrower")
        self.tabWidget.addTab(self.overview_tab, "")
        self.screenshot_tab = QtWidgets.QWidget()
        self.screenshot_tab.setObjectName("screenshot_tab")
        self.tabWidget.addTab(self.screenshot_tab, "")
        self.comtrade_tab = QtWidgets.QWidget()
        self.comtrade_tab.setObjectName("comtrade_tab")
        self.time_label = QtWidgets.QLabel(self.comtrade_tab)
        self.time_label.setGeometry(QtCore.QRect(0, 10, 151, 31))
        self.time_label.setAutoFillBackground(False)
        self.time_label.setAlignment(QtCore.Qt.AlignCenter)
        self.time_label.setWordWrap(False)
        self.time_label.setObjectName("time_label")
        self.device_label = QtWidgets.QLabel(self.comtrade_tab)
        self.device_label.setGeometry(QtCore.QRect(180, 10, 161, 31))
        self.device_label.setAlignment(QtCore.Qt.AlignCenter)
        self.device_label.setObjectName("device_label")
        self.wave_label = QtWidgets.QLabel(self.comtrade_tab)
        self.wave_label.setGeometry(QtCore.QRect(390, 10, 151, 31))
        self.wave_label.setAlignment(QtCore.Qt.AlignCenter)
        self.wave_label.setObjectName("wave_label")
        self.tabWidget.addTab(self.comtrade_tab, "")
        self.message_tab = QtWidgets.QWidget()
        self.message_tab.setObjectName("message_tab")
        self.tabWidget.addTab(self.message_tab, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.file_menu_bar = QtWidgets.QMenu(self.menubar)
        self.file_menu_bar.setObjectName("file_menu_bar")
        self.edit_menu_bar = QtWidgets.QMenu(self.menubar)
        self.edit_menu_bar.setObjectName("edit_menu_bar")
        self.help_menu_bar = QtWidgets.QMenu(self.menubar)
        self.help_menu_bar.setObjectName("help_menu_bar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.open_file_action = QtWidgets.QAction(MainWindow)
        self.open_file_action.setObjectName("open_file_action")
        self.open_folder_action = QtWidgets.QAction(MainWindow)
        self.open_folder_action.setObjectName("open_folder_action")
        self.close_folder_action = QtWidgets.QAction(MainWindow)
        self.close_folder_action.setObjectName("close_folder_action")
        self.exit_action = QtWidgets.QAction(MainWindow)
        self.exit_action.setObjectName("exit_action")
        self.about_action = QtWidgets.QAction(MainWindow)
        self.about_action.setObjectName("about_action")
        self.file_menu_bar.addAction(self.open_file_action)
        self.file_menu_bar.addAction(self.open_folder_action)
        self.file_menu_bar.addAction(self.close_folder_action)
        self.file_menu_bar.addSeparator()
        self.file_menu_bar.addAction(self.exit_action)
        self.help_menu_bar.addAction(self.about_action)
        self.menubar.addAction(self.file_menu_bar.menuAction())
        self.menubar.addAction(self.edit_menu_bar.menuAction())
        self.menubar.addAction(self.help_menu_bar.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.overview_tab), _translate("MainWindow", "概述"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.screenshot_tab), _translate("MainWindow", "截屏"))
        self.time_label.setText(_translate("MainWindow", "时间列表"))
        self.device_label.setText(_translate("MainWindow", "装置列表"))
        self.wave_label.setText(_translate("MainWindow", "波形列表"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.comtrade_tab), _translate("MainWindow", "录波"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.message_tab), _translate("MainWindow", "报文"))
        self.file_menu_bar.setTitle(_translate("MainWindow", "文件"))
        self.edit_menu_bar.setTitle(_translate("MainWindow", "编辑"))
        self.help_menu_bar.setTitle(_translate("MainWindow", "帮助"))
        self.open_file_action.setText(_translate("MainWindow", "打开文件"))
        self.open_folder_action.setText(_translate("MainWindow", "打开文件夹"))
        self.close_folder_action.setText(_translate("MainWindow", "关闭文件夹"))
        self.exit_action.setText(_translate("MainWindow", "退出"))
        self.about_action.setText(_translate("MainWindow", "关于"))