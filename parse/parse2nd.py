import ast

from models.funcnode import get_script
from models.sentencenode import SuspectedSentenceNode
from utils.funclink import ProjectAnalyzer


def add_sentence_purpose(sentence_node_list, file_name, line_no, private_info_list_to_be_added):
    """

        Args:
            sentence_node_list:
            file_name: 所被添加purpose 的sentence_node 的 文件名
            line_no: 所被添加purpose 的sentence_node 的 所在行
            private_info_list_to_be_added: 用于添加 purpose 的（datatype,purpose)元素对
        Returns:

        """
    for sentence_node in sentence_node_list:
        if sentence_node.file_path == file_name and sentence_node.line_no == line_no:
            private_info_without_usage = [info for info in sentence_node.private_info if info[1] != "None"]
            for pair in private_info_list_to_be_added:
                # private_info 添加
                private_info_each = [(private[0], pair[1]) for private in sentence_node.private_info if
                                     private[1] == "None" and pair[1] != "None"]
                private_info_without_usage.extend(private_info_each)
                # purpose 添加
                if pair[1] != "None" and pair[1] not in sentence_node.purpose:
                    sentence_node.purpose.append(pair[1])
            # sentence_node.purpose = [purpose for purpose in
            #                          sentence_node.purpose + [item[1] for item in private_info_list_to_be_added] if
            #                          purpose != "Usage"]
            if "None" in sentence_node.purpose:
                sentence_node.purpose.remove("None")
            # if len(sentence_node.purpose) != 0:
            #     sentence_node.purpose.remove("Usage")
            if private_info_without_usage:
                sentence_node.private_info = private_info_without_usage
            break


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


def parse_tree2nd(source_dir, p, node, lines, func_node_dict, node_list_1st, file_name, call_flow, node_list=None,
                  func_name=None,
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
    func_list = []  # node 中所有的方法
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
        func_call = []  # 该Func define node 调用的方法
        func_path = None
        if func_name is not None:
            func_path = file_name.replace("\\", '/').replace(
                source_dir.replace("\\", "/") + "/", '').replace('py',
                                                                 func_name).replace(
                '/', '.')
            if class_name is not None:
                func_path = file_name.replace("\\", '/').replace(
                    source_dir.replace("\\", '/') + "/", '').replace('py',
                                                  class_name + '.' + func_name).replace(
                    '/', '.')
            # print(func_path)
            # func_path = source_dir.split("\\")[-1] + "." + func_path
            # print(func_path)
            try:
                func_call = p.find_direct_callee_func(func_path)
            except:
                pass

        func_list = list(set(func_list))
        # 隐私类型传递   func{data，usage} 中data 为空，则将func.usage赋予data,usage else extend
        # c(): a.b   b中有隐私，赋给 c
        private_info = []
        for func in func_list:
            for func_c in func_call:
                if func == func_c.split('.')[-1]:
                    if func_c in func_node_dict.keys():
                        for pair in func_node_dict[func_c]:
                            if pair[0] != "None":
                                private_info.append(pair)
                        add_sentence_purpose(node_list_1st, file_name, node.lineno, func_node_dict[func_c])
                    # 增加call_flow
                    if func_c in p.get_methods():
                        if file_name + "#" + str(node.lineno) in call_flow.keys():
                            call_flow[file_name + "#" + str(node.lineno)].append(func_c)
                        else:
                            call_flow[file_name + "#" + str(node.lineno)] = [func_c]
        script = get_script(node, lines)

        if len(private_info) > 0:
            sentence_node = SuspectedSentenceNode(file_name, node.lineno, private_word_list=None, purpose=None,
                                                  func_name=func_name,
                                                  private_info=private_info, script=script)
            # print(private_info)
            has = False
            for node_1st in node_list_1st:
                if sentence_node == node_1st:
                    has = True
                    break
            if not has:
                node_list.append(sentence_node)

    if isinstance(node, ast.ClassDef):
        for node_son in node.body:
            node_list, call_flow = parse_tree2nd(source_dir, p, node_son, lines, func_node_dict, node_list_1st,
                                                 file_name, call_flow, node_list, func_name=node.name,
                                                 class_name=node.name)
    elif isinstance(node, ast.FunctionDef):
        for node_son in node.body:
            node_list, call_flow = parse_tree2nd(source_dir, p, node_son, lines, func_node_dict, node_list_1st,
                                                 file_name, call_flow, node_list, func_name=node.name,
                                                 class_name=class_name)
    else:
        try:
            for node_son in node.body:
                node_list, call_flow = parse_tree2nd(source_dir, p, node_son, lines, func_node_dict, node_list_1st,
                                                     file_name, call_flow, node_list, func_name=func_name,
                                                     class_name=class_name)
            #
            if isinstance(node, ast.If):
                for node_son in node.orelse:
                    node_list, call_flow = parse_tree2nd(source_dir, p, node_son, lines, func_node_dict, node_list_1st,
                                                         file_name, call_flow, node_list, func_name=func_name,
                                                         class_name=class_name)
        except AttributeError:
            pass

    return node_list, call_flow


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
    call_flow_list = {}
    for file_name in file_list:
        with open(file_name, encoding='utf-8') as file_single:
            lines = file_single.readlines()
            tree_root = ast.parse(''.join(lines))
            node_list_single, call_flow_single = parse_tree2nd(source, p, tree_root, lines, func_node_dict,
                                                               node_list1st, file_name, {})
            node_list.extend(node_list_single)
            call_flow_list.update(call_flow_single)
    return node_list, call_flow_list
