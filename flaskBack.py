from flask import Flask, request
from interface import annotate
from flask_cors import CORS
from flask import jsonify
from utils.fileio import load_json

app = Flask("PrivacyScan")

cors = CORS(app, resources={r"/scan": {"origins": "*"}})


@app.route("/scan", methods=['POST'])
def scan():
    source = request.get_json()['source']
    file_name = request.get_json()['fileName']
    data_type = load_json('lattices/datatype.json')
    purpose_dict = load_json('lattices/purpose.json')
    lattice = {'dataType': data_type, 'purpose': purpose_dict}

    result = annotate(source, lattice,file_name)
    # result = {
    #     'accuracy': {
    #         'recall_accurate': 10,
    #         'recall_location': 128,
    #         'location_num': 158
    #     },
    #     'missed': {
    #         'suspected_node_list': ["第一个文件 第一行", "第一个文件 第二行"],
    #         'missed': ["命中：第一个文件 第一行", "未命中：第二个文件第三行"]
    #     }
    # }
    res = jsonify(result)
    return res


if __name__ == '__main__':
    app.run()
