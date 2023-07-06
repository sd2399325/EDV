import os
import win32com.client as win32
from PyQt5.QtGui import QStandardItem, QColor
from PyQt5.QtCore import Qt

def convert_excel_to_html(input_file, output_file):
    """将Excel文件的除了"试验数据记录表"以外的sheet页转换为HTML文件

    Args:
        input_file (str): 目标Excel文件路径
        output_file (str): 生成HTML文件路径
    """
    # 判断输出文件是否已存在，若存在则删除
    if os.path.exists(output_file):
        os.remove(output_file)

    # 创建Excel应用程序对象
    excel = win32.gencache.EnsureDispatch('Excel.Application')

    try:
        # 获取输入文件的绝对路径
        input_file = os.path.abspath(input_file)

        # 打开Excel文件
        workbook = excel.Workbooks.Open(input_file)

        # 遍历所有sheet页
        for i in reversed(range(1, workbook.Sheets.Count + 1)):
            sheet = workbook.Sheets(i)
            if sheet.Name == "试验数据记录表":
                # 如果sheet页名称为"试验数据记录表"，则移除该sheet页
                workbook.Sheets(i).Delete()

        # 将剩余的sheet页保存为HTML格式
        output_file = os.path.abspath(output_file)
        workbook.SaveAs(output_file, FileFormat=44)

        # 关闭工作簿
        workbook.Close(SaveChanges=False)

    except Exception as e:
        print(f"转换Excel文件失败：{e}")

    finally:
        # 关闭Excel应用程序
        excel.Quit()

def split_txt_line(txt_line, event_levels_colors):
    """拆分txt文件中的一行数据

    Args:
        txt_line (str): txt文档中的一行数据
        event_levels_colors (str): 枚举事件登记和颜色
    """
    data = txt_line.split()

    # 处理时间信息
    time = ' '.join(data[:2])

    # 获取报文信息
    host = data[2]

    # 处理系统警告
    alarm = data[3]

    # 处理事件等级和报警组的粘连情况
    level, group = split_string(data[4], event_levels_colors.keys())

    # 处理事件列表
    events = ' '.join(data[5:])

    # 创建QStandardItem，并设置对应的颜色
    item_time = QStandardItem(time)
    item_host = QStandardItem(host)
    item_alarm = QStandardItem(alarm)
    item_level = QStandardItem(level)
    item_group = QStandardItem(group)
    item_events = QStandardItem(events)

    # 根据事件等级设置对应的颜色
    color = QColor(event_levels_colors.get(level))
    item_time.setBackground(color)
    item_host.setBackground(color)
    item_alarm.setBackground(color)
    item_level.setBackground(color)
    item_group.setBackground(color)
    item_events.setBackground(color)

    return [item_time, item_host, item_alarm, item_level, item_group, item_events]

def split_string(level_group, enum_values):
    """事件等级和报警组的粘连

    Args:
        level_group (str): 事件等级和报警组信息
        enum_values (str): 枚举事件等级
    """
    result = ['', '']  # 初始化拆分结果为两个空字符串

    for value in enum_values:
        if level_group.startswith(value):
            result[0] = value
            result[1] = level_group[len(value):].strip()
            break

    return result