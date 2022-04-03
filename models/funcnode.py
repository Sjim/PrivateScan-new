import ast
import re

from algorithm.charactermatch import word_match
from lattices.asttype import ast_type
from utils.fileio import load_json
from models.sentencenode import SuspectedSentenceNode


def go_split(s, symbol):
    """
        将代码行的内容分解成单词列表

    Args:
        s: script
        symbol: 分隔符

    Returns:


    """
    result = [s]
    for i in symbol:
        median = []
        for z in map(lambda x: x.split(i), result):
            median.extend(z)
        result = median
    return [x.replace(' ', '') for x in result if x not in [':\n', '']]


def get_params(node, node_params=None):
    """
    获取赋值语句中的函数参数
        例如："request1, request2 = a + b"
        return 的内容为 request1, request2
        node(a,b)
        return a,b
    Args:
        node:ast node
        node_params:[]

    Returns:
        [request1, request2]

    """
    if not node_params:
        node_params = []
    if isinstance(node, ast.Name):
        node_params.append(node.id)
        return node_params
    elif isinstance(node, ast.Call):
        for arg in node.args:
            if isinstance(arg, ast.Name):
                node_params.append(arg.id)
            else:
                node_params = get_params(arg, node_params)
    elif isinstance(node, ast.List) or isinstance(node, ast.Tuple) or isinstance(node, ast.Set):
        for arg in node.elts:
            if isinstance(arg, ast.Name):
                node_params.append(arg.id)
            else:
                node_params = get_params(arg, node_params)
    else:
        pass
    return node_params


def get_script(node, script_list):
    """

    Args:
        node: ast节点
        script_list:源代码字符串列表

    Returns:

    """
    script_ori = script_list[node.lineno - 1:node.end_lineno]
    script_tmp = ""
    if node.__class__ in ast_type:
        for i in range(len(script_ori)):
            if ":" not in script_ori[i]:
                script_tmp = script_tmp + script_ori[i].replace('\\\n', '').replace('\n', '')
            else:
                script_tmp = script_tmp + script_ori[i]
                break
    else:
        script_tmp = "".join(script_ori).replace('\\\n', '').replace('\n', '')
    words_list = {'methods': [], 'vars': []}
    get_all_words(node, node.lineno, words_list)

    words_in_line = go_split(script_tmp, '.()[]{},=+-*/#&@!^\'\" ')

    words_list['vars'] = [item for item in words_list['vars'] if
                          item not in words_list['methods'] and item in words_in_line]
    # print(words_list)
    words_list['methods'] = [item for item in words_list['methods'] if
                             item in words_in_line]
    words_list['methods'] = list(set(words_list['methods']))
    words_list['vars'] = list(set(words_list['vars']))
    # print(node.lineno, words_list)
    # words_list['methods'] = go_split(script_tmp, '()[]{},=+-*/#&@!^ ')
    # words_list['vars'] = go_split(script_tmp, '()[]{},=+-*/#&@!^ ')
    return script_tmp, words_list


def match_data_type(script, data_type):
    """

    Args:
        script: 代码字符串
        data_type: 隐私数据类型

    Returns:
        [(data_type, word_in script),...]

    """
    private_word_list = []

    for word in script:
        for key in data_type.keys():
            word_std_list = data_type[key]['abbr']
            if word_match(word_std_list, word):
                private_word_list.append((key, word))
    private_word_list = list(set(private_word_list))
    return private_word_list


def match_purpose_type(script, purpose_dict):
    """

    Args:
        script:
        purpose_dict:

    Returns:
        purpose

    """
    purpose = []
    for word in script:
        for key in purpose_dict.keys():
            purpose_list = purpose_dict[key]['abbr']
            if word_match(purpose_list, word):
                purpose.append(purpose_dict[key]['path'])
    purpose = list(set(purpose))
    if len(purpose) == 0:
        purpose = ["Usage"]
    return purpose


def get_all_words(node, line_no, vars_and_methods):
    if isinstance(node, ast.Call):
        name = ""
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        vars_and_methods['methods'].append(name)
    # if hasattr(node, 'lineno') and node.lineno == line_no:
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):  # 添加所有单词作为变量
                    vars_and_methods['vars'].append(item)
                if isinstance(item, ast.AST):
                    get_all_words(item, line_no, vars_and_methods)
        elif isinstance(value, str):  # 添加所有单词作为变量
            vars_and_methods['vars'].append(value)
        elif isinstance(value, ast.AST):
            get_all_words(value, line_no, vars_and_methods)


def get_all_vars(node, line_no, var_list):
    if node.lineno == line_no:

        # recursion
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        get_all_vars(item, line_no, var_list)
            elif isinstance(value, ast.AST):
                get_all_vars(value, line_no, var_list)


# todo: 优化
class FuncNode:
    def __init__(self, func_node, file_path, lattices, script_list=None):
        self.func_node = func_node
        self.file_path = file_path
        self.script_list = script_list
        self.private_info = []
        self.key_variable = {}
        self.func_name = func_node.name
        self.lattices = lattices

    def get_sentence_nodes(self, node=None, all_nodes=None):
        """

        Args:
            node: ast_node
            all_nodes: all suspected sentence node

        Returns:

        """
        if node is None:
            node = self.func_node
        if all_nodes is None:
            all_nodes = []

        line_no = node.lineno
        data_type = self.lattices["dataType"]
        purpose_dict = self.lattices["purpose"]

        script_ori, script = get_script(node, self.script_list)
        # print(script)

        private_word_list = match_data_type(script['vars'], data_type)
        for var in script['vars']:
            if var in self.key_variable:
                private_word_list.extend(self.key_variable[var][0])
        private_word_list = list(set(private_word_list))
        if len(private_word_list) == 0:
            private_word_list = [("Data", "data")]

        purpose = match_purpose_type(script['methods'] + script['vars'], purpose_dict)
        if not (("Data", "data") in private_word_list and purpose == ["Usage"]):
            sentence_node = SuspectedSentenceNode(self.file_path, line_no, private_word_list, purpose,
                                                  script=script_ori)
            # print(private_word_list, purpose)
            all_nodes.append(sentence_node)
            # 考虑数据流，找到赋值语句，将被隐私数据污染的数据保存到private_word_list
            # TODO
            if isinstance(node, ast.Assign):
                if len(private_word_list) > 0:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.key_variable[target.id] = (private_word_list, purpose)
                        elif isinstance(target, ast.Attribute):
                            self.key_variable[target.attr] = (private_word_list, purpose)
                        else:
                            pass
                else:
                    node_params = get_params(node.value)
                    for node_param in node_params:
                        if node_param in list(self.key_variable.keys()):
                            private_word_list_inherit, purpose_inherit = self.key_variable[node_param]
                            sentence_node = SuspectedSentenceNode(self.file_path, line_no,
                                                                  private_word_list_inherit,
                                                                  purpose_inherit, script=script_ori)
                            all_nodes.append(sentence_node)
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    self.key_variable[target.id] = (private_word_list_inherit, purpose_inherit)
                                elif isinstance(target, ast.Attribute):
                                    self.key_variable[target.attr] = (private_word_list_inherit, purpose_inherit)
                                elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                                    self.key_variable[target.value.id] = (private_word_list_inherit, purpose_inherit)
                                else:
                                    pass

            elif isinstance(node, ast.Expr):
                # TODO 逻辑
                node_params = get_params(node.value)
                if len(node_params) > 0:
                    for node_param in node_params:
                        if node_param in list(self.key_variable.keys()) and len(private_word_list) == 0:
                            private_word_list_inherit, purpose_inherit = self.key_variable[node_param]
                            sentence_node = SuspectedSentenceNode(self.file_path, line_no,
                                                                  private_word_list_inherit,
                                                                  purpose_inherit, script=script_ori)
                            all_nodes.append(sentence_node)

        for private_word in private_word_list:
            if not (private_word[0] == "Data" and purpose[0] == "Usage") and private_word[0] not in [info[0] for info in
                                                                                                     self.private_info]:
                for p in purpose:
                    self.private_info.append((private_word[0], p))

        node_son_list = []
        for field, value in ast.iter_fields(node):
            if field == "body" or field == "orelse":
                node_son_list.append(value)

        if len(node_son_list) > 0:
            for field in node_son_list:
                for node_son in field:
                    all_nodes = self.get_sentence_nodes(node_son, all_nodes)

        return all_nodes

    def __str__(self):
        return self.script_list[0]


if __name__ == '__main__':
    file = open("D:\\study\\python\\cmdb-python-master\\test.py", encoding='utf-8')
    lines = file.readlines()
    string = ""
    for line in lines:
        string += line
    node = ast.parse(string)
    words_list = {'methods': [], 'vars': []}
    get_all_words(node.body[1].body[0], 5, words_list)
    print(words_list)
