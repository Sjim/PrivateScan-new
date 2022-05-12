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
    print(request.get_json())
    data_type = load_json('lattices/datatype_dictionary.json')
    purpose_dict = load_json('lattices/purpose_dictionary.json')
    lattice = {'dataType': data_type, 'purpose': purpose_dict}

    result = annotate(source, lattice,
             False)
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
    print(source)
    return jsonify(result)


if __name__ == '__main__':
    app.run()
