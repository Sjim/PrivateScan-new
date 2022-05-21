import xlwt

from utils.fileio import load_location, write_json


def out_analyze(node_list, source, save_file: str, entire=False):
    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet("DataType")

    cols = ["Location", "Function", "DataType", "Purpose"]
    if entire:
        cols.remove("Function")

    for i in range(len(cols)):
        sheet.write(0, i, cols[i])

    tmp_row = 1
    for i in range(len(node_list)):
        node = node_list[i]
        file_path = node.file_path.replace('\\', '/').replace(source.replace('\\', '/') + '/', '').split('/')[-1]
        location = file_path + "#L" + str(node.line_no)

        for data_type, purpose in node.private_info:
            if not data_type:
                data_type = "None"
            if not purpose:
                purpose = "None"
            if not node.func_name:
                node.func_name = "None"
            sheet.write(tmp_row, 0, location)
            if not entire:
                sheet.write(tmp_row, 1, node.func_name)
                sheet.write(tmp_row, 2, data_type)
                sheet.write(tmp_row, 3, purpose)
            else:
                sheet.write(tmp_row, 1, data_type)
                sheet.write(tmp_row, 2, purpose)
            tmp_row += 1

    book.save(save_file)
