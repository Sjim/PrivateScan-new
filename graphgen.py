import graphviz
import pyan

from utils import fileio

# root_dir1 = "/Users/liufan/program/PYTHON/SAP/PrivacyScan/systementrance.py"
# root_dir2 = "/Users/liufan/program/PYTHON/SAP/PrivacyScan/utils/fileio.py"
# root_list = [root_dir2, root_dir1]

source_dir = "/Users/liufan/program/PYTHON/SAP/PrivacyScan"
file_list = fileio.walk_files_path(source_dir)

res = pyan.create_callgraph(file_list, format="dot")

graph = graphviz.Source(res)
graph.view()
