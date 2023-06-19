import sys
import json
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QDialogButtonBox

class RenameDialog(QDialog):

    def __init__(self, current_name, project_path, root_path):
        super().__init__()
        self.setWindowTitle("重命名")
        self.setFixedSize(300, 200)  # 固定窗体大小
        self.layout = QVBoxLayout()

        # 创建标签和输入框
        self.label = QLabel("请输入新的工程名称：")
        self.line_edit = QLineEdit()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)

        # 创建按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

        # 保存当前名称和项目路径
        self.current_name = current_name
        self.project_path = project_path
        self.root_path = root_path

    def accept(self):
        # 获取用户输入的新的工程名称
        new_name = self.line_edit.text()

        # 更新配置文件中的路径信息
        with open('rename.json', 'r') as f:
            data = json.load(f)

        # 检查是否存在相同的 current_name 和 item_path
        for entry in data:
            if entry["original_name"] == self.current_name and entry["file_path"] == self.project_path:
                entry["new_name"] = new_name
                break
        else:
            # 添加新的重命名信息
            new_entry = {
                "original_name": self.current_name,
                "new_name": new_name,
                "file_path": self.project_path,
                "root_path": self.root_path
            }
            data.append(new_entry)

        # 更新 rename.json 文件
        with open('rename.json', "w") as f:
            json.dump(data, f, indent=4)

        super().accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    current_name = "file1.txt"  # 当前名称
    project_path = "/path/to/file1.txt"  # 项目路径
    root_path = "/path/to"  # 根路径

    dialog = RenameDialog(current_name, project_path, root_path)
    dialog.exec_()

    sys.exit(app.exec_())
