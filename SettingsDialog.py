import sys
import json
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout,QDialogButtonBox

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("设置")
        self.layout = QVBoxLayout()

        # 创建标签和输入框
        self.label = QLabel("录波软件路径：")
        self.line_edit = QLineEdit()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)

        # 创建按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def accept(self):
        # 获取用户输入的路径信息
        path = self.line_edit.text()

        # 更新配置文件中的路径信息
        with open('config.json', 'r+') as f:
            config = json.load(f)
            config['wave_app'] = path
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()

        super().accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = SettingsDialog()
    dialog.exec_()

    sys.exit(app.exec_())
