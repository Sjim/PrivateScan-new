import os
import time

from accuracy.accuracytest import test_recall_accuracy, test_stamp
from accuracy.accuracytest import test_missed
from analyze.outanalyze import out_analyze
from parse.parse import parse_files
from parse.parse2nd import parse_files_2nd
from models.funcnode import match_data_type
from utils.fileio import load_json, write_csv, write_to_excel
from utils.funclink import get_link, get_call_flow
from utils.source import get_file_list
from utils import log

logging = log.getlogger()


def get_program_purpose(source, lattices, func_node_dict):
    program_name = source.replace("\\", '/').split("/")[-1]
    # 项目名称中有purpose 作为 项目的purpose
    purpose = match_data_type(program_name, lattices['purpose'])
    data_type = match_data_type(program_name, lattices['dataType'])
    if purpose[0][0] != "None":
        return purpose[0]
    # 项目名称中有datatype 找datatype对应的purpose作为项目的purpose
    elif data_type[0] != ("None", "none"):
        for private_info_pair in func_node_dict.values():
            for pair in private_info_pair:
                if pair[0] == data_type[0]:
                    return data_type[1]
    else:
        for key, value in func_node_dict.items():
            if key.endswith("main"):
                main_purpose = [item[1] for item in value]
                dict_num = {}
                for item in main_purpose:
                    if item not in dict_num.keys():
                        dict_num[item] = main_purpose.count(item)
                # print(dict_num)
                most_counter = sorted(dict_num.items(), key=lambda x: x[1], reverse=True)[0][0]
                return most_counter
    empty = []
    for l in func_node_dict.values():
        empty.extend(l)
    all_purpose = [item[1] for item in empty]
    dict_num = {}
    for item in all_purpose:
        if item not in dict_num.keys():
            dict_num[item] = all_purpose.count(item)
    # print(dict_num)
    most_counter = sorted(dict_num.items(), key=lambda x: x[1], reverse=True)[0][0]
    return most_counter


def test_projects(_path, _lattice):
    projects = os.listdir(_path)
    for project in projects:
        if project != ".idea" and project != ".DS_Store":
            project_path = _path + '/' + project
            stamp, func_node_dict = annotate(
                project_path,
                lattice, False)
            print(project)
            for s in stamp:
                print(s)
            save_path = 'analyze/output/' + project.replace('.py', '') + '.xls'
            write_to_excel(stamp, save_path)
    # print(os.listdir(_path))


def annotate(source, lattices, entire=False):
    """

    Args:
        source: file_name which can be directory, file, zip
        lattices: _
        entire: 是否打印完整结果

    Returns:

    """
    # 获取文件列表（文件名）
    logging.warning("Start getting file list...")
    source, file_list = get_file_list(source)
    logging.warning("Start getting all operations for private info and methods call graph...")
    # 解析文件，获取隐私数据操作 和 函数调用图
    node_list, func_dict = parse_files(file_list, source, lattices)
    # print("func_dict", func_dict)

    # 递归获取所有方法可能的隐私数据和操作
    logging.warning("Start getting suspected data and operations in the first recursion...")
    func_node_dict = get_link(func_dict, source)
    # 第二遍递归
    logging.warning("Start second recursion...")
    node_list2nd = parse_files_2nd(file_list, source, func_node_dict,
                                   node_list)

    # 将第二次递归对内容添加到列表
    node_list.extend(node_list2nd)
    # 去重wqq
    node_list_no_repeated = []
    node_string = [node.__str__() for node in node_list]
    for node in node_list:
        if node_string.count(node.__str__()) == 1:
            node_list_no_repeated.append(node)
        else:
            node_string.remove(node.__str__())

    for node in node_list:
        print(node)
    # 计算准确率
    logging.warning("Start calculate the accuracy...")

    stamp = [(node.file_path.replace("\\", "/").replace(source + "/", ''), node.line_no, node.private_info,
              node.private_word_list) for node in
             node_list_no_repeated]
    # 隐私扫描结果输出到json文件
    logging.warning("Output the result into file...")

    # todo 处理annotation 的 返回值
    if not entire:
        out_analyze(node_list_no_repeated, source, "analyze/output/" + source.split("\\")[-1] + ".xls", entire)
        call_flow = get_call_flow(source)
        anno = []
        for value in func_node_dict.values():
            for pair in value:
                item = {"dataType": {"value": pair[0], "confidence": 1}, "purpose": {"value": pair[1], "confidence": 1}}
                if item not in anno:
                    anno.append(item)
        return anno, call_flow
    else:
        # 当entire 为true
        purpose = get_program_purpose(source, lattices, func_node_dict)
        node_list_filtered = [item for item in node_list_no_repeated if
                              item.purpose is not None and
                              purpose in item.purpose]
        out_analyze(node_list_filtered, source, "analyze/output/" + source.split("\\")[-1] + ".xls", entire)
        data_type_list = []
        for item in node_list_filtered:
            for data_type_each in item.private_word_list:
                if data_type_each != ("None", "none") and {"dataType": data_type_each[0], "confidence": 1} not in data_type_list:
                    data_type_list.append({"dataType": data_type_each[0], "confidence": 1})
        return {"dataType": data_type_list, "purpose": purpose}


if __name__ == '__main__':
    data_type = load_json('lattices/datatype.json')
    purpose_dict = load_json('lattices/purpose.json')
    lattice = {'dataType': data_type, 'purpose': purpose_dict}

    # res = annotate("D:\\Download\\azure-storage-blob-master\\sdk\\storage\\azure-storage-file-share\\samples", lattice, False)

    # annotate("D:\\study\\python\\cmdb-python-master", lattice, True)
    annotate("D:\\study\\python\\test", lattice, False)
    # annotate("D:\\study\\python\\PrivateInformationScanning", lattice, False)
    # func_node_dict, call_flow = annotate("D:\\study\\python\\SAP检测项目\\nnja-python\\pyworkshop",
    #                                      lattice, False)
    # func_node_dict = annotate("D:\\study\\python\\SAP检测项目\\roytuts-python",
    #                                      lattice, False)
    # print('----------------annotation-------------------')
    # for key, value in func_node_dict.items():
    #     print(key, value)
    # print('----------------call-flow-------------------')
    # for key, value in call_flow.items():
    #     print(key, value)


