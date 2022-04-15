import ast
import re
from models.funcnode import FuncNode, get_script, match_data_type, \
    match_purpose_type
from models.sentencenode import SuspectedSentenceNode
from utils import log

logging = log.getlogger()


def parse_tree(source, lattices, file_name, tree_node, code_lines, node_list=None, func_dict=None, class_name=None):
    """

    Args:
        source: 项目路径
        lattices: 隐私类型
        file_name: 文件名（单个）
        tree_node: ast节点
        code_lines: 源代码字符（readlines（））
        node_list: sentencenode列表
        func_dict: 函数调用字典
        class_name: 方法类名

    Returns:

    """
    if func_dict is None:
        func_dict = {}
    if node_list is None:
        node_list = []
    data_type = lattices["dataType"]
    purpose_dict = lattices["purpose"]
    if isinstance(tree_node, ast.FunctionDef):
        func_node = FuncNode(tree_node, file_name, lattices, code_lines)
        try:
            all_nodes = func_node.get_sentence_nodes()
        except AttributeError:
            raise AttributeError(file_name, tree_node.lineno)

        node_list.extend(all_nodes)
        if len(func_node.private_info) > 0:
            source_replace = source.replace('\\', '/')
            if class_name is None:
                func_path = func_node.file_path.replace("\\", '/').replace(
                    source_replace + '/', '').replace('.py',
                                                      '/' + func_node.func_name).replace(
                    '/', '.')
            else:
                func_path = func_node.file_path.replace("\\", '/').replace(
                    source_replace + '/', '').replace('.py',
                                                      '/' + class_name + "/" + func_node.func_name).replace(
                    '/', '.')
            func_dict[func_path] = func_node.private_info

    elif isinstance(tree_node, ast.ClassDef):
        class_name = tree_node.name
        for node_son in tree_node.body:
            if isinstance(node_son, ast.FunctionDef):
                node_list, func_dict = parse_tree(source, lattices, file_name, node_son, code_lines, node_list,
                                                  func_dict, class_name)
    # elif not isinstance(tree_node, ast.Module):
    #     line_no = tree_node.lineno
    #     script_ori, script = get_script(tree_node, code_lines)
    #
    #     private_word_list = match_data_type(script['vars'], data_type)
    #     private_word_list = list(set(private_word_list))
    #
    #     # print(script['methods'])
    #     purpose = match_purpose_type(script['methods'], purpose_dict)
    #     if not (("None", "none") in private_word_list and purpose == ["None"]):
    #         sentence_node = SuspectedSentenceNode(file_name, line_no,
    #                                               private_word_list, purpose, None,
    #                                               script=script_ori)
    #         # print(private_word_list, purpose)
    #         node_list.append(sentence_node)
    try:
        for node_son in tree_node.body:
            node_list, func_dict = parse_tree(source, lattices, file_name, node_son, code_lines,
                                              node_list, func_dict)
    except AttributeError:
        pass
    return node_list, func_dict


def parse_files(file_list, source, lattices):
    """

    Args:
        file_list: 文件名列表
        source: 文件路径
        lattices: 隐私类型

    Returns:
        node_list:[<models.sentencenode.SuspectedSentenceNode object at 0x10e786eb0>,
         <models.sentencenode.SuspectedSentenceNode object at 0x10e786f10>]
         node_list为sentencenode对象列表，sentencenode对象可打印。

         [sentencenode1, sentencenode2...]

        func_node_dict:  {'sdk_api.saltstack.SaltAPI.__init__': [('PassWord', 'Usage')],
         'sdk_api.saltstack.SaltAPI.token_id': [('UserName', 'Usage'), ('PassWord', 'Usage')],
         'sdk_api.saltstack.__init__': [('PassWord', 'Usage')],

         {func_path:[(private_info, purpose), ...]}

    """
    node_list = []
    func_dict = {}
    for file_name in file_list:
        with open(file_name, encoding='utf-8') as file_single:
            logging.error("Constructing file to ast:" + file_name)
            lines = file_single.readlines()
            file_string = re.sub(r"if[ ]*__name__[ ]*==[ ]*['\"]__main__['\"]", "def main()", ''.join(lines))
            try:
                tree_root = ast.parse(file_string)
            except SyntaxError as e:
                logging.error("Syntax error in "+file_name)
            node_list_single, func_dict = parse_tree(source, lattices, file_name, tree_root, lines, func_dict=func_dict)
            node_list.extend(node_list_single)
    return node_list, func_dict


if __name__ == '__main__':
    # print(re.sub(r"if[ ]*__name__[ ]*==[ ]*['\"]__main__['\"]", "def main()", "if __name__ == '__main__'"))
    # print(re.sub(r"if[ ]*__name__[ ]*==[ ]*['\"]__main__['\"]", "def main()", "if __name__==\"__main__\""))
    # print("if __name__==\"__main__\"".replace(r"if[ ]*__name__[ ]*==[ ]*['\"]__main__['\"]", "def main()"))
    with open("/Users/liufan/program/PYTHON/SAP/privacyScanLsn/test/main.py", encoding='utf-8') as file_single:
        lines = file_single.read()
        # print(lines)
        # ast.parse(lines)
        tree_root = ast.parse(lines)
        print(lines)
