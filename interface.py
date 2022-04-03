import os
import time

from accuracy.accuracytest import test_recall_accuracy, test_stamp
from accuracy.accuracytest import test_missed
from analyze.outanalyze import out_analyze
from parse.parse import parse_files
from parse.parse2nd import parse_files_2nd
from utils.fileio import load_json, write_csv, write_to_excel
from utils.funclink import get_link
from utils.source import get_file_list
from utils import log

logging = log.getlogger()


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
    # print("func_node_dict", func_node_dict)
    # print(func_node_dict)
    # for nodes in node_list:
    #     print(nodes)
    # 第二遍递归
    logging.warning("Start second recursion...")
    node_list2nd = parse_files_2nd(file_list, source, func_node_dict,
                                   node_list)

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
    # 计算准确率
    logging.warning("Start calculate the accuracy...")
    # ac = test_recall_accuracy(node_list_no_repeated, source)

    stamp = [(node.file_path.replace("\\", "/").replace(source + "/", ''), node.line_no, node.private_info,
              node.private_word_list) for node in
             node_list_no_repeated]
    # 隐私扫描结果输出到json文件
    logging.warning("Output the result into file...")
    # out_analyze(node_list, source)

    # todo
    # if not entire:
    #     pass
    # else:
    #     pass
    return stamp, func_node_dict


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


if __name__ == '__main__':
    data_type = load_json('lattices/datatype.json')
    purpose_dict = load_json('lattices/purpose.json')
    lattice = {'dataType': data_type, 'purpose': purpose_dict}
    # test_projects("/Users/liufan/program/PYTHON/SAP/TestProject", lattice)
    time_start = time.time()
    # print(time_start)
    stamp, func_node_dict = annotate("/Users/liufan/program/PYTHON/SAP/cmdb-python-master", lattice, False)
    print(time.time() - time_start)
    # for key, value in func_node_dict.items():
    #     print(key, value)
    # for s in stamp:
    #     print(s)
    # write_to_excel(stamp, r'analyze/output/cmdb-python-master.xls')

    # test_stamp(stamp)
    # print("---------------------------")
    # for key, value in func_node_dict.items():
    #     print(key, value)
    # write_to_excel(stamp)
    # res = annotate("D:\\Download\\azure-storage-blob-master\\sdk\\storage\\azure-storage-file-share\\samples", lattice, False)

    # annotate("D:\\study\\python\\cmdb-python-master\\cmdb\\views\\test", lattice, False)
