import ast

from models.funcnode import get_script
from models.sentencenode import SuspectedSentenceNode
from utils.funclink import ProjectAnalyzer


def get_func_list(node, func_list=None):
    """

    Args:
        node: ast_node
        func_list: 代码调用的方法列表

    Returns:

    """
    if func_list is None:
        func_list = []
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            func_list.append(node.func.attr)
        elif isinstance(node.func, ast.Name):
            func_list.append(node.func.id)
        if len(node.args) > 0:
            for arg in node.args:
                func_list = get_func_list(arg, func_list)
    elif isinstance(node, ast.List) or isinstance(node, ast.Tuple) or isinstance(node, ast.Set):
        for arg in node.elts:
            func_list = get_func_list(arg, func_list)
    elif isinstance(node, ast.Compare):
        for comp in node.comparators:
            func_list = get_func_list(comp, func_list)
        func_list = get_func_list(node.left, func_list)
    elif isinstance(node, ast.withitem):
        func_list = get_func_list(node.context_expr)
    return func_list


def parse_tree2nd(source_dir, p, node, lines, func_node_dict, node_list_1st, file_name, node_list=None, func_name=None,
                  class_name=None):
    """

    Args:
        source_dir: -
        p: 函数调用关系的类
        node: -
        lines: -
        func_node_dict: 全项目函数调用图
        node_list_1st: 第一次便利结果
        file_name: -
        node_list: -
        func_name: -
        class_name: -

    Returns:

    """
    if node_list is None:
        node_list = []
    func_list = []
    if isinstance(node, ast.Expr) or isinstance(node, ast.Assign) or isinstance(node, ast.Return):
        func_list = get_func_list(node.value)
    elif isinstance(node, ast.For):
        func_list = get_func_list(node.iter)
    elif isinstance(node, ast.While) or isinstance(node, ast.If):
        func_list = get_func_list(node.test)
    elif isinstance(node, ast.With):
        for item in node.items:
            func_list = get_func_list(item, func_list)

    if len(func_list) > 0:
        func_call = []
        func_path = None
        if func_name is not None:
            func_path = file_name.replace(source_dir + "\\", '').replace("\\", '/').replace('py', func_name).replace(
                '/', '.')
            if class_name is not None:
                func_path = file_name.replace(source_dir + "\\", '').replace("\\", '/').replace('py',
                                                                                                class_name + '.' + func_name).replace(
                    '/', '.')
            try:
                func_call = p.find_direct_callee_func(func_path)
            except:
                pass

        func_list = list(set(func_list))
        # 隐私类型传递
        private_info = []
        for func in func_list:
            for func_c in func_call:
                if func == func_c.split('.')[-1] and func_c in func_node_dict.keys():
                    private_info.extend(func_node_dict[func_c])
        script = get_script(node, lines)

        if len(private_info) > 0:
            sentence_node = SuspectedSentenceNode(file_name, node.lineno, private_word_list=None, purpose=None,
                                                  private_info=private_info, script=script)
            has = False
            for node_1st in node_list_1st:
                if sentence_node == node_1st:
                    has = True
                    break
            if not has:
                node_list.append(sentence_node)
    if isinstance(node, ast.ClassDef):
        for node_son in node.body:
            node_list = parse_tree2nd(source_dir, p, node_son, lines, func_node_dict, node_list_1st,
                                      file_name, node_list, func_name=node.name, class_name=node.name)
    elif isinstance(node, ast.FunctionDef):
        for node_son in node.body:
            node_list = parse_tree2nd(source_dir, p, node_son, lines, func_node_dict, node_list_1st,
                                      file_name, node_list, func_name=node.name, class_name=class_name)
    else:
        try:
            for node_son in node.body:
                node_list = parse_tree2nd(source_dir, p, node_son, lines, func_node_dict, node_list_1st,
                                          file_name, node_list, func_name=func_name,
                                          class_name=class_name)
        except AttributeError:
            pass

    return node_list


def parse_files_2nd(file_list, source, func_node_dict, node_list1st):
    """

    Args:
        file_list: -
        source: -
        func_node_dict:函数调用图
        node_list1st: 第一次遍历结果

    Returns:
        -
    """
    p = ProjectAnalyzer(source)
    node_list = []
    for file_name in file_list:
        with open(file_name, encoding='utf-8') as file_single:
            lines = file_single.readlines()
            tree_root = ast.parse(''.join(lines))
            node_list_single = parse_tree2nd(source, p, tree_root, lines, func_node_dict, node_list1st, file_name)
            node_list.extend(node_list_single)
    return node_list
