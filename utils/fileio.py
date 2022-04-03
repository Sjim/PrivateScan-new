import csv
import os
import json

# TODO 增加文件传输的方式（文件夹、文件、数据流）
import xlrd
import xlwt


def write_csv(node_list):
    with open("tmp_res.csv", "w", newline="") as file:
        csvwriter = csv.writer(file, dialect=("excel"))
        # csv文件插入一行数据，把下面列表中的每一项放入一个单元格（可以用循环插入多行）
        csvwriter.writerows(node_list)


def walk_files(path, endpoint='.py'):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(endpoint):
                file_list.append(open(file_path, encoding='utf-8'))

    return file_list


def walk_files_path(path, endpoint='.py'):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(endpoint):
                file_list.append(file_path)
    return file_list


def load_json(json_file):
    with open(json_file, 'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict


def write_json(json_file, data):
    with open(json_file, 'w') as file:
        file.write(json.dumps(data))


def load_location(file_path):
    wk_bk = xlrd.open_workbook(file_path)
    wk_all = wk_bk.sheet_by_index(0)

    location_list = [(location.split('/')[0].replace('.py', '').replace('.', '/') + '.py', int(location.split('/')[1]))
                     for location in list(wk_all.col_values(0))[2:] if location != '']

    datatype_list = [data_type.split('/')[-1] for data_type in wk_all.col_values(1)[2:] if data_type != '']

    purpose_list = [purpose for purpose in wk_all.col_values(2)[2:] if purpose != '']

    location_dict = {}
    for i in range(len(location_list)):
        if location_list[i] in location_dict.keys():
            location_dict[location_list[i]].append((datatype_list[i], purpose_list[i]))
        else:
            location_dict[location_list[i]] = [(datatype_list[i], purpose_list[i])]

    # print(len(location_dict.items()))
    # for item, value in location_dict.items():
    #     print(item, value)
    # print(location_dict)

    return


def write_to_excel(stamp, file_path):
    book = xlwt.Workbook(encoding='utf-8')
    sheet_datatype = book.add_sheet("DataType")
    sheet_purpose = book.add_sheet("Purpose")

    sheet_datatype.write(0, 0, "Location")
    sheet_datatype.write(0, 1, "DataType")
    sheet_datatype.write(0, 2, "confidence")
    sheet_datatype.write(0, 3, "Script")

    sheet_purpose.write(0, 0, "Location")
    sheet_purpose.write(0, 1, "Purpose")
    sheet_purpose.write(0, 2, "confidence")
    sheet_purpose.write(0, 3, "Script")

    i = 1
    j = 1
    for st in stamp:
        loc = st[0] + ' ' + str(st[1])
        datatype = list(set([data[0] for data in st[2] if data[0] != 'Data']))
        purpose = list(set([data[1] for data in st[2] if data[1] != 'Usage']))
        for data in datatype:
            sheet_datatype.write(i, 0, loc)
            sheet_datatype.write(i, 1, data)
            sheet_datatype.write(i, 2, 1)
            i += 1
        for pur in purpose:
            sheet_purpose.write(j, 0, loc)
            sheet_purpose.write(j, 1, pur)
            sheet_purpose.write(j, 2, 1.0 / len(purpose))
            j += 1

    book.save(file_path)


def list_to_excel(file_path, data_type_list, purpose_list):
    book = xlwt.Workbook(encoding='utf-8')
    sheet_datatype = book.add_sheet("DataType")
    sheet_purpose = book.add_sheet("Purpose")

    sheet_datatype.write(0, 0, "Location")
    sheet_datatype.write(0, 1, "DataType")
    sheet_datatype.write(0, 2, "confidence")
    sheet_datatype.write(0, 3, "Script")

    sheet_purpose.write(0, 0, "Location")
    sheet_purpose.write(0, 1, "Purpose")
    sheet_purpose.write(0, 2, "confidence")
    sheet_purpose.write(0, 3, "Script")

    i = 1
    j = 1
    for data in data_type_list:
        sheet_datatype.write(i, 0, data[0])
        sheet_datatype.write(i, 1, data[1])
        sheet_datatype.write(i, 2, 1)
        i += 1
    for pur in purpose_list:
        sheet_purpose.write(j, 0, pur[0])
        sheet_purpose.write(j, 1, pur[1])
        sheet_purpose.write(j, 2, 1)
        j += 1

    book.save(file_path)


def load_data_purpose_split(file_path):
    wk_bk = xlrd.open_workbook(file_path)
    wk_all = wk_bk.sheet_by_index(0)

    data_type_list = []
    purpose_list = []
    for i in range(2, wk_all.nrows):
        path = wk_all.row_values(i)[0]
        data_type = wk_all.row_values(i)[1]
        purpose = wk_all.row_values(i)[2]
        if path != '':
            path = path.replace('/', ' ').replace('.', '/').replace('/py', '.py')
        if data_type != '' and data_type != 'any':
            data_type_list.append((path, data_type.split('/')[-1]))
        if purpose != 'Usage' and purpose != '':
            purpose_list.append((path, purpose))

    return data_type_list, purpose_list
