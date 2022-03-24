import xlrd

from utils.fileio import load_location


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


if __name__ == '__main__':
    load_location("项目校对表.xlsx")
