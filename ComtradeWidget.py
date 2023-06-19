import os
import json
import subprocess
import locale
from datetime import datetime
from PyQt5.QtWidgets import (
    QTreeView, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QSplitter
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QModelIndex
from natsort import natsorted


class ComtradeWidget(QWidget):
    global_dict = {}
    global_time_set = set()
    global_device_set = set()
    global_device_dic = {}
    global_wave_dic = {}
    global_wave_path = ""
    global_time_info = ""

    def __init__(self, wave_path):
        super().__init__()

        # 创建主部件和布局
        main_layout = QHBoxLayout(self)

        # 创建 QSplitter 控件
        splitter = QSplitter(self)


        # 创建三个QWidget 控件用来装在layout
        time_widget = QWidget()
        device_widget = QWidget()
        waveform_widget = QWidget()

        # 创建三个垂直布局
        time_layout = QVBoxLayout(time_widget)
        device_layout = QVBoxLayout(device_widget)
        waveform_layout = QVBoxLayout(waveform_widget)

        # 创建三个 QTreeView 控件和 QLabel 控件
        self.time_tree = QTreeView()
        self.device_tree = QTreeView()
        self.waveform_tree = QTreeView()

        time_label = QLabel("时间列表")
        device_label = QLabel("装置列表")
        waveform_label = QLabel("波形列表")

        # 设置标签的样式
        label_style = "background-color: lightblue; font-size: 14px; font-weight: bold; border-radius: 5px;"
        time_label.setStyleSheet(label_style)
        device_label.setStyleSheet(label_style)
        waveform_label.setStyleSheet(label_style)

        # 设置标签文本居中对齐
        time_label.setAlignment(Qt.AlignCenter)
        device_label.setAlignment(Qt.AlignCenter)
        waveform_label.setAlignment(Qt.AlignCenter)

        # 设置时间列表的根节点为 "事件列表"
        self.time_model = QStandardItemModel()
        root_item = self.time_model.invisibleRootItem()
        root_item.setEditable(False)
        root_item.setText("事件列表")

        # 设置 time_tree 的数据模型
        self.time_tree.setModel(self.time_model)
        self.time_tree.header().setVisible(False)
        self.time_tree.expandAll()  # 展开所有节点
        self.time_tree.setExpandsOnDoubleClick(False)  # 禁止双击收起节点

        # 自定义样式表，调整节点之间的间距和节点文字字体大小
        self.style_sheet = """
            QTreeView {
                background-color: gray;
            }
            QTreeView::item {
                padding: 8px;
                font-size: 16px;
            }
        """
        self.time_tree.setStyleSheet(self.style_sheet)

        # 设置节点点击事件的处理函数
        self.time_tree.clicked.connect(self.load_device_tree)
        self.device_tree.clicked.connect(self.load_waveform_tree)

        # 设置节点双击事件处理函数
        self.waveform_tree.doubleClicked.connect(self.open_wave_app)

        # 将控件添加到布局中
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_tree)
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_tree)
        waveform_layout.addWidget(waveform_label)
        waveform_layout.addWidget(self.waveform_tree)

        self.device_tree.setStyleSheet(self.style_sheet)
        # 设置 time_tree 和 device_tree 的水平大小策略
        self.time_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.device_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 将QWidget 控件添加到 QSplitter 控件中
        splitter.addWidget(time_widget)
        splitter.addWidget(device_widget)
        splitter.addWidget(waveform_widget)
        splitter.setOrientation(Qt.Horizontal)
        splitter.setSizes([self.width() * 0.25, self.width() * 0.25,self.width() * 0.50])
        splitter.setLineWidth(0)

        # 将splitter 控件添加到主布局中
        main_layout.addWidget(splitter)

        # 加载时间列表的数据
        self.load_time_tree(wave_path)

    def load_time_tree(self, wave_path):
        if not wave_path:
            return None

        self.global_wave_path = wave_path
        self.find_time(wave_path)

        # 清空时间列表的数据
        self.time_model.removeRows(0, self.time_model.rowCount())
        self.device_tree.setModel(QStandardItemModel())
        self.waveform_tree.setModel(QStandardItemModel())

        # 查找时间key并填充控件
        for time_info in self.global_time_set:
                time_format = self.convert_time(time_info)
                time_item = QStandardItem()
                time_item.setTextAlignment(Qt.AlignCenter)
                time_item.setText(time_format)
                time_item.setData(time_info, Qt.UserRole)
                time_item.setFlags(Qt.ItemIsEnabled)
                self.time_model.appendRow(time_item)

    def load_device_tree(self, index):
        device_model = QStandardItemModel()
        device_root_item = device_model.invisibleRootItem()
        device_root_item.setEditable(False)

        # 获取点击的节点
        self.global_time_info = index.data(Qt.UserRole)

        if self.global_time_info is None:
            return

        self.find_device(self.global_time_info)
        wave_model = QStandardItemModel()
        self.waveform_tree.setModel(wave_model)

        for folder in self.global_device_dic:
            folder_item = QStandardItem()
            folder_item.setTextAlignment(Qt.AlignCenter)
            folder_item.setText(folder)
            folder_item.setData(folder, Qt.UserRole)
            folder_item.setFlags(Qt.ItemIsEnabled)
            device_model.appendRow(folder_item)

            for device in self.global_device_dic[folder]:
                device_item = QStandardItem()
                device_item.setTextAlignment(Qt.AlignCenter)
                device_item.setText(device)
                device_item.setData(device, Qt.UserRole)
                device_item.setFlags(Qt.ItemIsEnabled)
                folder_item.appendRow(device_item)



        # 设置 device_tree 的数据模型
        self.device_tree.setModel(device_model)
        self.device_tree.header().setVisible(False)
        self.device_tree.expandAll()
        self.device_tree.setExpandsOnDoubleClick(False)
        self.device_tree.setStyleSheet(self.style_sheet)

    def load_waveform_tree(self, index):
        # 获取点击的节点
        item = index.model().itemFromIndex(index)
        if item is None:
            return

        # 判断节点的层级
        if item.parent() is None:
            # 一级节点，跳出
            return

        # 遍历文件夹路径下的文件夹和文件
        waveform_model = QStandardItemModel()
        waveform_root_item = waveform_model.invisibleRootItem()
        waveform_root_item.setEditable(False)

        # 获取设备信息
        device_info = item.data(Qt.UserRole)
        if device_info is None:
            return

        self.find_wave(device_info)

        # 获取波形信息
        for time_str in self.global_wave_dic.keys():
            time_info = self.convert_time(time_str)
            time_item = QStandardItem()
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setText(time_info)
            time_item.setData(time_info, Qt.UserRole)
            time_item.setFlags(Qt.ItemIsEnabled)
            waveform_model.appendRow(time_item)

            for wave_info in self.global_wave_dic[time_str]:
                wave_item = QStandardItem()
                wave_item.setTextAlignment(Qt.AlignCenter)
                wave_item.setText(wave_info[0])
                wave_item.setData(wave_info[1], Qt.UserRole)
                wave_item.setFlags(Qt.ItemIsEnabled)
                time_item.appendRow(wave_item)

        # 设置 waveform_tree 的数据模型
        self.waveform_tree.setModel(waveform_model)
        self.waveform_tree.header().setVisible(False)
        self.waveform_tree.expandAll()
        self.waveform_tree.setExpandsOnDoubleClick(False)
        self.style_waveform = """
            QTreeView {
                background-color: #e4e4e4;
            }
            QTreeView::item {
                padding: 8px;
                font-size: 16px;
            }
        """
        self.waveform_tree.setStyleSheet(self.style_waveform)

    def load_waveform_items(self, folder_path, parent_item):
        for entry_name in os.listdir(folder_path):
            entry_path = os.path.join(folder_path, entry_name)
            entry_item = QStandardItem()
            entry_item.setTextAlignment(Qt.AlignCenter)
            entry_item.setText(entry_name)
            entry_item.setData(entry_path, Qt.UserRole)
            entry_item.setFlags(Qt.ItemIsEnabled)
            parent_item.appendRow(entry_item)

            if os.path.isdir(entry_path):
                # 如果是文件夹，递归加载子文件夹和.cfg文件
                self.load_waveform_items(entry_path, entry_item)
            elif entry_name.endswith(".cfg"):
                # 如果是.cfg文件，创建子节点并显示
                cfg_item = QStandardItem()
                cfg_item.setTextAlignment(Qt.AlignCenter)
                cfg_item.setText("Config File: " + entry_name)
                cfg_item.setData(entry_path, Qt.UserRole)
                entry_item.appendRow(cfg_item)

    def open_wave_app(self, index):
        # 获取点击的节点
        item = index.model().itemFromIndex(index)
        if item is None:
            return

        # # 判断节点的层级
        # if item.parent() is None:
        #     # 一级节点，跳出
        #     return

        # 获取 cfg 文件路径
        cfg_file_path = item.data(Qt.UserRole)

        # 读取配置文件中的波形应用程序路径
        config_file = "config.json"
        tfrplot_path = "tfrplot_tool.exe"
        arguments = [cfg_file_path]
        if os.path.exists(config_file):
            with open(config_file) as f:
                config_data = json.load(f)
                wave_app_path = config_data.get("wave_app")
                if wave_app_path:
                    command = [tfrplot_path] + arguments
                    subprocess.run(command)

    def find_time(self, wave_path):
        """查找时间"""
        time_info_set = set()
        for root, dirs, files in os.walk(wave_path):
             for file in files:
                if file.endswith(".CFG"):
                    # 提取时间信息
                    parts = file.split('_')
                    time_info = '_'.join(parts[4:7])
                    if time_info not in time_info_set:
                        time_info_set.add(time_info)

        self.global_time_set = natsorted(time_info_set)

    def find_device(self, time_info):
        """查找设备"""
        self.global_device_dic.clear()
        for root, dirs, files in os.walk(self.global_wave_path):
            for file in files:
                if file.endswith(".CFG") and time_info in file:
                    parts = file.split('_')
                    device_info = ""
                    # 获取设备信息
                    if '-' in parts[1]:
                        device_info = [part for part in parts[1].split('-') if part != '' and part != 'S1'][0]
                    else:
                        device_info = parts[1]


                    # 获取文件夹信息
                    fold_info = root.split('\\')[-3]
                    if self.global_device_dic and fold_info in self.global_device_dic:
                        dic_values = self.global_device_dic[fold_info]
                        if device_info not in dic_values:
                            self.global_device_dic[fold_info].append(device_info)
                    else:
                        devices = []
                        devices.append(device_info)
                        self.global_device_dic[fold_info] = devices

    def find_wave(self, device_info):
        """查找波形"""
        # {时间key:{波形key:路径value}}
        # 增加一级节点用的时间key
        wave_fino_dic = {}
        wave_info_dic= {}

        for root, dirs, files in os.walk(self.global_wave_path):
            for file in files:
                if file.endswith(".CFG") and device_info in file:
                    # 提取录波文件信息和路径
                    parts = file.split('_')
                    time_info = '_'.join(parts[4:7])
                    wave_info = parts[-1]
                    cfg_file_path = os.path.join(root, file)
                    wave_info_dic[wave_info] = cfg_file_path
                    sort_dic = natsorted(wave_info_dic.items(), key=lambda x: x[0])
                    wave_fino_dic[time_info] = sort_dic

        self.global_wave_dic = wave_fino_dic

    def convert_time(self, time_info_str):
        """转换时间格式"""
        locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
        dt = datetime.strptime(time_info_str, '%Y%m%d_%H%M%S_%f')
        time_info = dt.strftime('%Y年%m月%d日 %H:%M:%S.%f')[:-3]
        return time_info
