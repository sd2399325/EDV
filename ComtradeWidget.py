import os
import json
import subprocess
from PyQt5.QtWidgets import (
    QTreeView, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
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

        # 创建三个垂直布局
        time_layout = QVBoxLayout()
        device_layout = QVBoxLayout()
        waveform_layout = QVBoxLayout()

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
            QTreeView::item {
                padding: 8px;  /* 调整节点之间的间距 */
                font-size: 16px;  /* 调整节点文字的字体大小 */
            }
        """
        self.time_tree.setStyleSheet(self.style_sheet)

        # 设置节点点击事件的处理函数
        self.time_tree.clicked.connect(self.load_device_tree)
        self.device_tree.clicked.connect(self.load_waveform_tree)

        # 设置节点双击事件处理函数
        self.device_tree.doubleClicked.connect(self.open_wave_app)
        self.waveform_tree.doubleClicked.connect(self.open_wave_app)

        # 将控件添加到布局中
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_tree)
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_tree)
        waveform_layout.addWidget(waveform_label)
        waveform_layout.addWidget(self.waveform_tree)

        # 设置 time_tree 和 device_tree 的水平大小策略
        self.time_tree.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.device_tree.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # 将垂直布局添加到主布局
        main_layout.addLayout(time_layout)
        main_layout.addLayout(device_layout)
        main_layout.addLayout(waveform_layout)

        # 加载时间列表的数据
        self.load_time_tree(wave_path)

    def load_time_tree(self, wave_path):
        if not wave_path:
            return None

        self.global_wave_path = wave_path
        self.find_time(wave_path)

        # 清空时间列表的数据
        self.time_model.removeRows(0, self.time_model.rowCount())

        # 查找时间key并填充控件
        for time_info in self.global_time_set:
                time_item = QStandardItem()
                time_item.setTextAlignment(Qt.AlignCenter)
                time_item.setText(time_info)
                time_item.setFlags(Qt.ItemIsEnabled)
                self.time_model.appendRow(time_item)

    def load_device_tree(self, index):
        device_model = QStandardItemModel()
        device_root_item = device_model.invisibleRootItem()
        device_root_item.setEditable(False)

        # 获取点击的节点
        self.global_time_info = index.data(Qt.DisplayRole)

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

        self.find_wave(self.global_time_info, device_info)

        # 获取波形信息
        for wave_info in self.global_wave_dic.keys():
            wave_item = QStandardItem()
            wave_item.setTextAlignment(Qt.AlignCenter)
            wave_item.setText(wave_info)
            wave_item.setData(self.global_wave_dic[wave_info], Qt.UserRole)
            wave_item.setFlags(Qt.ItemIsEnabled)
            waveform_model.appendRow(wave_item)

        # 设置 waveform_tree 的数据模型
        self.waveform_tree.setModel(waveform_model)
        self.waveform_tree.header().setVisible(False)
        self.waveform_tree.setExpandsOnDoubleClick(False)
        self.waveform_tree.setStyleSheet(self.style_sheet)

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
                    # 获取设备信息
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


    def find_wave(self, time_info, device_info):
        wave_fino_dic = {}
        for root, dirs, files in os.walk(self.global_wave_path):
            for file in files:
                if file.endswith(".CFG") and time_info in file and device_info in file:
                    # 提取录波文件信息和路径
                    parts = file.split('_')
                    wave_info = '_'.join(parts[3:])
                    cfg_file_path = os.path.join(root, file)
                    wave_fino_dic[wave_info] = cfg_file_path

        self.global_wave_dic = wave_fino_dic


