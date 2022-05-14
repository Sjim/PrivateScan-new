import os
import time

from flask import jsonify

from accuracy.accuracytest import test_recall_accuracy, test_stamp
from accuracy.accuracytest import test_missed
from analyze.outanalyze import out_analyze
from lattices.buildtree import switch_dict
from parse.parse import parse_files, add_code_outside_func
from parse.parse2nd import parse_files_2nd
from models.funcnode import match_data_type
from utils.fileio import load_json, write_csv, write_to_excel
from utils.funclink import get_link, get_call_flow
from utils.source import get_file_list
from utils import log
from utils.ERRORLIST import error_list

logging = log.getlogger()


def get_program_purpose(source, lattices, func_node_dict, node_list):
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
            if key.endswith("main") or key.endswith("__main__"):
                main_purpose = [item[1] for item in value]
                dict_num = {}
                for item in main_purpose:
                    if item not in dict_num.keys():
                        dict_num[item] = main_purpose.count(item)
                # print(dict_num)
                most_counter = sorted(dict_num.items(), key=lambda x: x[1], reverse=True)[0][0]
                return most_counter
    empty = []
    for l in node_list:
        empty.extend(l.purpose)

    dict_num = {}
    for item in empty:
        if item not in dict_num.keys():
            dict_num[item] = empty.count(item)
    # print(dict_num)
    if node_list:
        most_counter = sorted(dict_num.items(), key=lambda x: x[1], reverse=True)[0][0]
    else:
        most_counter = None
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
    logging.warning("Start getting file list...")
    lattices = switch_dict(lattices)
    source, file_list = get_file_list(source)
    # print(source, file_list)
    logging.warning("Start getting all operations for private info and methods call graph...")
    # 解析文件，获取隐私数据操作 和 函数调用图
    node_list, func_dict = parse_files(file_list, source, lattices)
    # print("func_dict", func_dict)
    if entire or not entire:  # 当entire 为True时 要检测方法外代码行
        node_list = add_code_outside_func(file_list, lattices, node_list)
    # 递归获取所有方法可能的隐私数据和操作
    logging.warning("Start getting suspected data and operations in the first recursion...")
    func_node_dict = get_link(func_dict, source, file_list)
    # 第二遍递归
    logging.warning("Start second recursion...")
    node_list2nd = parse_files_2nd(file_list, source, func_node_dict,
                                   node_list)
    # try:
    #     # 获取文件列表（文件名）
    #
    # except Exception as e:
    #     # 因为有各种报错 包括编译错误SyntaxError 包循环依赖导致的KeyError 以及可能出现的其他error 具体信息都在e中 就直接返回e 而不返回具体文件名和行数
    #
    #     logging.error(
    #         "Error happened in " + e.__traceback__.tb_frame.f_globals["__file__"] + str(e.__traceback__.tb_lineno))
    #     return {"correctness": False, "result": e}
    if error_list:
        return {"correctness": False, "result": error_list}
    # 将第二次递归对内容添加到列表
    node_list.extend(node_list2nd)
    # 去重
    node_list_no_repeated = []
    node_string = [node.__str__() for node in node_list]
    for node in node_list:
        if node_string.count(node.__str__()) == 1:
            node_list_no_repeated.append(node)
        else:
            node_string.remove(node.__str__())

    # for node in node_list_no_repeated:
    #     print(node)

    # 计算准确率
    logging.warning("Start calculate the accuracy...")
    # 隐私扫描结果输出到json文件
    logging.warning("Output the result into file...")
    return_value = {"correctness": True, "result": {}}
    if not entire:
        out_analyze(node_list_no_repeated, source,
                    "analyze/output2/" + source.replace('\\', '/').split("/")[-1] + ".xls", entire)
        call_flow = get_call_flow(source, file_list)
        anno = {}
        for key, value in func_node_dict.items():
            anno[key] = []
            for pair in value:
                item = {"dataType": {"value": pair[0], "confidence": 1}, "purpose": {"value": pair[1], "confidence": 1}}
                if item not in anno[key]:
                    anno[key].append(item)
        return_value['result'].update(annotation=anno, call_flow=call_flow)

    else:
        # 当entire 为true
        purpose = get_program_purpose(source, lattices, func_node_dict, node_list_no_repeated)
        node_list_filtered = [item for item in node_list_no_repeated if
                              item.purpose is not None and
                              purpose in item.purpose]
        out_analyze(node_list_filtered, source, "analyze/output2/" + source.replace('\\', '/').split("/")[-1] + ".xls",
                    entire)
        data_type_list = []
        for item in node_list_filtered:
            for data_type_each in item.private_word_list:
                if data_type_each != ("None", "none") and {"dataType": data_type_each[0],
                                                           "confidence": 1} not in data_type_list:
                    data_type_list.append({"dataType": data_type_each[0], "confidence": 1})
        return_value['result'] = {"dataType": data_type_list, "purpose": purpose}
    return return_value


if __name__ == '__main__':
    data_type = load_json('lattices/datatype.json')
    purpose_dict = load_json('lattices/purpose.json')
    lattice = {'dataType': data_type, 'purpose': purpose_dict}

    # res = annotate("D:\\Download\\azure-storage-blob-master\\sdk\\storage\\azure-storage-file-share\\samples", lattice,
    #                False)
    res = annotate("/Users/liufan/Documents/实验室/隐私扫描项目/SAP检测项目/roytuts-python/python-record-my-voice",lattice,False)
    print('----------------annotation-------------------')
    for key, value in res['result']['annotation'].items():
        print(key, value)
    print('----------------call-flow-------------------')
    for key, value in res['result']['call_flow'].items():
        print(key, value)
