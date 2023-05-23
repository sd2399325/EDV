from openpyxl import load_workbook

def read_excel(file_path):
    """
    读取试验概述数据excel文件
    # param file_path: 文件路径
    """
    workbook = load_workbook(file_path)
    sheet_names = workbook.sheetnames

    result = []
    for sheet_name in sheet_names:
        sheet = workbook[sheet_name]
        data = []
        for row in sheet.iter_rows(values_only=True):
            data.append(row)
        result.append({sheet_name: data})

    return result