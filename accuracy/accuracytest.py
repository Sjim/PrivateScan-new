import xlrd

from utils.fileio import load_location, load_data_purpose_split, list_to_excel


def test_recall_accuracy(suspected_node_list, source):
    """
    查全率=（检索出的相关信息量/系统中的相关信息总量）
    :param suspected_node_list:
    :param source:
    :return:
    """
    location_dict = load_location("项目校对表-旧.xlsx")
    location_num = len(location_dict.keys())
    recall_location = 0
    recall_accurate = 0
    print("准确的结果如下：")
    for node in suspected_node_list:
        if node.private_info is None:
            node.private_info = [(key_word[0], node.purpose) for key_word in node.private_word_list]
        print((node.file_path.replace(source + '\\', ''), node.line_no, node.private_info,node.purpose))
        if (node.file_path.replace(source + '\\', '').replace("\\", '/'), node.line_no) in location_dict.keys():
            recall_location += 1
            # print(node)
            # print(location_dict[(node.file_path.replace(source + '/', ''), node.line_no)])
            # print()

            if node.private_info == location_dict[
                (node.file_path.replace(source + '\\', '').replace("\\", '/'), node.line_no)]:
                recall_accurate += 1
    if recall_location>0:
        print("查全率为： ", recall_accurate, "/", recall_location, '/', location_num, '/', recall_location / location_num)
        print("查准率为： ", recall_accurate, "/", recall_location, '/', len(suspected_node_list), '/',
              recall_location / len(suspected_node_list))
    return {"recall_accurate": recall_accurate, "recall_location": recall_location, "location_num": location_num}


def test_missed(suspected_node_list, source):
    location_dict = load_location("项目校对表-旧.xlsx")
    paths = [(node.file_path.replace(source + "\\", '').replace("\\", "/"), node.line_no) for node in
             suspected_node_list]
    res = []
    for node in location_dict.keys():
        if node not in paths:
            # print("未命中：" + node[0] + str(node[1]))
            res.append("未命中：" + node[0] + str(node[1]))
        else:
            # print("命中：" + node[0] + str(node[1]))
            res.append("命中：" + node[0] + str(node[1]))
    paths = [paths[0],paths[1],]
    return {"suspected_node_list": paths, "missed": res}


def test_stamp(stamp):
    # print(stamp)
    data_type_compute = []
    purpose_compute = []
    for st in stamp:
        loc = st[0] + ' ' + str(st[1])
        datatype = list(set([data[0] for data in st[2] if data[0] != 'Data']))
        purpose = list(set([data[1] for data in st[2] if data[1] != 'Usage']))
        for dt in datatype:
            data_type_compute.append((loc, dt))
        for pur in purpose:
            purpose_compute.append((loc, pur))

    data_type_list, purpose_list = load_data_purpose_split("/Users/liufan/program/PYTHON/SAP/privacyScanLsn/项目校对表-旧.xlsx")

    for data in data_type_list:
        if data not in data_type_compute:
            print(data)

    for pur in purpose_list:
        if pur not in purpose_compute:
            print(pur)

    data_type_all = list(set(data_type_compute + data_type_list))
    purpose_all = list(set(purpose_list + purpose_compute))

    print("data_type准确率为： ", len(data_type_compute), "/", len(data_type_all),
          len(data_type_compute) / len(data_type_all))
    print("purpose准确率为： ", len(purpose_compute), "/", len(purpose_all),
          len(purpose_compute) / len(purpose_all))

    list_to_excel(r'analyze/output/cmdb-python-master-标准.xls', data_type_all, purpose_all)


if __name__ == '__main__':
    # load_location("项目校对表.xlsx")
    test_stamp()
