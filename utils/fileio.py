import csv
import os
import json

# TODO 增加文件传输的方式（文件夹、文件、数据流）
import xlrd


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

    return location_dict
