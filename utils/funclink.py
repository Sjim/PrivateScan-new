import ast
import copy
import logging
import os
import re
from _ast import AST
import numpy as np

import graphviz
import pyan

from utils.fileio import verify_file_list


class ProjectAnalyzer:
    def __init__(self, project, file_list):
        tmpfile = "./tmp.gv"
        self._clazzs = find_all_class(file_list, project=project)
        file_list = verify_file_list(file_list)
        graghviz(tmpfile, file_list)
        # _methods:函数名
        # _method_matrix:直接调用矩阵
        # 行:被调用者
        # 列:调用者
        self._methods, self._method_matrix = analyze_gv(tmpfile, project=project, endpoint=".py",
                                                        class_exclude=self._clazzs)
        # _matrix:可达性矩阵
        # _mediate:中间节点矩阵
        self._matrix = copy.deepcopy(self._method_matrix)
        self._mediate = algorithm(self._matrix)

    def get_methods(self):
        return self._methods

    def get_class(self):
        return self._clazzs

    def find_direct_callee_func(self, target_func=None):
        dimension = len(self._methods)
        if target_func is None:
            # 找出所有函数的直接callee
            result = {}
            for i in range(dimension):
                result[self._methods[i]] = []
            for i in range(dimension):
                for j in range(dimension):
                    if self._method_matrix[j][i] > 0:
                        result[self._methods[i]].append(self._methods[j])
            return result
        else:
            # 找出特定函数的直接callee 通过find
            # index = -1
            # for i in self._methods:
            #     if i.endswith(target_func):
            #         index = self._methods.index(i)
            #         break

            index = self._methods.index(target_func)
            if index < 0:
                raise Exception("no such method")
            result = []
            for i in range(dimension):
                if self._method_matrix[i][index] > 0:
                    result.append(self._methods[i])
            return result

    def find_direct_call_func(self, target_func=None):
        dimension = len(self._methods)
        if target_func is None:
            # 找出所有函数的直接caller
            result = {}
            for i in range(dimension):
                result[self._methods[i]] = []
            for i in range(dimension):
                for j in range(dimension):
                    if self._method_matrix[i][j] > 0:
                        result[self._methods[i]].append(self._methods[j])
            return result
        else:
            # 找出特定函数的直接caller
            index = self._methods.index(target_func)

            if index < 0:
                raise Exception("no such method")
            result = []
            for i in range(dimension):
                if self._method_matrix[index][i] > 0:
                    result.append(self._methods[i])
            return result

    def find_all_call_func(self, target_func):
        dimension = len(self._methods)
        index = self._methods.index(target_func)
        if index < 0:
            raise Exception("no such method")
        result = []
        for i in range(dimension):
            if self._matrix[index][i] > 0:
                callpath = algorithm2(self._matrix, self._mediate, index, i)
                result.append((self._methods[i], list(reversed([self._methods[x] for x in callpath]))))
        return result


def find_all_class(file_list: list, project="", endpoint=".py"):
    result = []
    for f in file_list:
        with open(f, 'r', encoding='utf8') as file:
            lines = file.readlines()
            tree = ast.parse(''.join(lines))
            for node in tree.body:
                part_result = find_class(node)
                for i in range(len(part_result)):
                    pa = part_result[i]
                    pa = (f[len(project) + 1:len(f) - len(endpoint)] + os.path.sep + pa).replace(os.path.sep, ".")
                    part_result[i] = pa
                result.extend(part_result)

    return result


def find_class(node: AST):
    if not isinstance(node, ast.ClassDef):
        return []
    else:
        result = [node.name]
        for son in node.body:
            result.extend(find_class(son))
        return result


def analyze_gv(gv, project="", endpoint=".py", class_exclude=None):
    method_adjacency = []
    methods = []
    clazzs = [] if class_exclude is None else class_exclude
    with open(gv, 'r') as gv_file:
        # 遍历找到所有的函数依赖关系
        gv_file.seek(0, 0)
        for line in gv_file.readlines():
            is_dependency = re.search(r'style="solid"', line)
            # is_import_file = re.search(r'__')
            if is_dependency is None:
                # 函数定义，不是函数依赖
                continue
            match_group = re.search(r'([a-zA-Z0-9_]+)\s*->\s*([a-zA-Z0-9_]+)', line)
            if match_group is not None:
                origin = match_group.group(1).replace("__", ".")
                target = match_group.group(2).replace("__", ".")
                # 去除私有方法
                flag1 = match_group.group(1).find("____") >= 0
                flag2 = match_group.group(2).find("____") >= 0

                # 去除类
                flag3 = origin in clazzs
                flag4 = target in clazzs
                # 去除依赖文件
                flag5 = os.path.isfile(project + "/" + match_group.group(1).replace("__", "/") + endpoint)
                flag6 = os.path.isfile(project + "/" + match_group.group(2).replace("__", "/") + endpoint)

                if not flag1 and not flag3:
                    if flag5:
                        origin += ".main"
                    if origin not in methods:
                        methods.append(origin)
                if not flag2 and not flag4:
                    if flag6:
                        target += ".main"
                    if target not in methods:
                        methods.append(target)

                if flag6 or flag1 or flag2 or flag3 or flag4:
                    continue

                method_adjacency.append((methods.index(target),
                                         methods.index(origin)))

    method_num = len(methods)
    method_matrix = [[0] * method_num for _ in range(method_num)]
    for adjacency in method_adjacency:
        method_matrix[adjacency[0]][adjacency[1]] = 1
    return methods, method_matrix


"""
matrix1:原始矩阵(直接调用关系)
return:中间节点矩阵
"""


def algorithm(matrix):
    # 可达性矩阵
    dimension = len(matrix)
    # 中间节点矩阵
    mediate_matrix = [[0] * dimension for _ in range(dimension)]
    # n三次方次迭代
    for i in range(dimension):
        for j in range(dimension):
            if matrix[j][i] > 0:
                for k in range(dimension):
                    if matrix[j][k] == 0 and matrix[i][k] > 0:
                        matrix[j][k] = 1
                        mediate_matrix[j][k] = i
    return mediate_matrix


"""
matrix1:可达性矩阵
matrix2:中间节点矩阵
return:可达路径(包括起点终点)
"""


def algorithm2(matrix1, matrix2, start, end):
    if matrix1[start][end] == 0:
        # 不可达
        return ()
    else:
        mediate = matrix2[start][end]
        if mediate == 0:
            # 可达，无中间节点
            return start, end
        # 可达，有中间节点
        left = list(algorithm2(matrix1, matrix2, start, mediate))
        right = list(algorithm2(matrix1, matrix2, mediate, end))
        left.pop()
        left.extend(right)
        return left


def test_algorithm():
    matrix = [[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
    algorithm(matrix)
    print(matrix)


def graghviz(output, args: list):
    try:
        res = pyan.create_callgraph(args, format="dot")
        with open(output, 'w') as f:
            f.write(res)
    except Exception as e:
        logging.error(str(e))
        raise e


def walk_files_path(path, endpoint='.py'):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(endpoint):
                file_list.append(file_path)
    return file_list


def get_link(func_node_dict, source_dir, file_list):
    func_node_dict_all = {}
    for key in func_node_dict.keys():
        func_node_dict_all[key] = func_node_dict[key]

    pa = ProjectAnalyzer(source_dir, file_list)
    for method in func_node_dict.keys():
        if method in pa.get_methods():
            for method_link in (pa.find_all_call_func(method)):
                if func_node_dict_all[method][0][0] == "None" and method_link[0] in func_node_dict.keys():
                    private_info_without_usage = [info for info in func_node_dict_all[method_link[0]] if
                                                  info[1] != "None"]
                    for pair in func_node_dict_all[method]:
                        # private_info 添加
                        private_info_each = [(private[0], pair[1]) for private in func_node_dict_all[method_link[0]]
                                             if
                                             private[1] == "None" and pair[1] != "None"]
                        private_info_without_usage.extend(private_info_each)
                    func_node_dict_all[method_link[0]] = private_info_without_usage

                else:
                    for pair in func_node_dict_all[method]:
                        if method_link[0] in func_node_dict.keys():
                            func_node_dict_all[method_link[0]].append(pair)
                        else:
                            # print(method, method_link[0])
                            func_node_dict_all[method_link[0]] = [pair]

    return func_node_dict_all


def get_call_flow(source_dir, file_list):
    func_flow = {}
    pa = ProjectAnalyzer(source_dir, file_list)
    for method in pa.get_methods():
        func_call = pa.find_direct_callee_func(method)
        if func_call:
            func_flow[method] = func_call
    return func_flow


def test():
    try:
        file_list = walk_files_path("D:\\Download\\kafka-python-master-X")
        res = pyan.create_callgraph(file_list, format="dot")
    except Exception as e:
        print(str(e))
        raise e
    return res


if __name__ == '__main__':
    # p = ProjectAnalyzer("/Users/liufan/program/PYTHON/SAP/cmdb-python-master")
    # print(p.get_methods())
    # print(p.find_all_call_func("sdk_api.saltstack.SaltAPI.post_reques"))
    # print(p.find_direct_callee_func().keys())
    # for key, value in p.find_direct_callee_func().items():
    #     print(key, value)
    # print(p.find_direct_callee_func())
    # try:
    #     test()
    # except KeyError as e:
    #     print(str(e))
    file_list = walk_files_path("/Users/liufan/program/PYTHON/SAP/TestProject")
    graghviz("111.gv", "/Users/liufan/program/PYTHON/SAP/TestProject/test.py")