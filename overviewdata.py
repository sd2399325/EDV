from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

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
        rows = sheet.max_row
        columns = sheet.max_column

        sheet_data = []
        for row in range(1, rows + 1):
            row_data = []
            for column in range(1, columns + 1):
                cell = sheet.cell(row=row, column=column)

                if cell.coordinate in sheet.merged_cells:
                    # 对于合并单元格，获取合并区域的左上角单元格的值
                    for merged_range in sheet.merged_cells.ranges:
                        if cell.coordinate in merged_range:
                            start_cell = merged_range.start_cell
                            row_data.append(sheet[start_cell.coordinate].value)
                            break
                else:
                    row_data.append(cell.value)

            sheet_data.append(row_data)

        result[sheet_name] = sheet_data

    return result