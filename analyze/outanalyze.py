from utils.fileio import load_location, write_json


def out_analyze(node_list, source):
    location_dict = load_location("项目校对表.xlsx")
    manual_data = {}
    for key, value in location_dict.items():
        manual_data[key[0] + ' ' + str(key[1])] = value
    manual_data_sorted = []
    for key in sorted(manual_data.keys()):
        for datatype, purpose in manual_data[key]:
            manual_data_sorted.append({
                "Location": key,
                "DataType": datatype,
                "Purpose": purpose,
                "Script": ""
            })

    node_info_list = {}
    for node in node_list:
        node_info_list[node.file_path.replace(source+'/', '')+' '+str(node.line_no)] = [node.private_info, node.script, node.confidence]

    node_info_list_sorted = []
    for key in sorted(node_info_list.keys()):
        for datatype, purpose in node_info_list[key][0]:
            confidence = 1
            if node_info_list[key][2] < 1:
                confidence = node_info_list[key][2]
            node_info_list_sorted.append({
                "Location": key,
                "DataType": datatype,
                "Purpose": purpose,
                "confidence": confidence,
                "Script": ""
            })

    write_json("manual.json", manual_data_sorted)
    write_json("program.json", node_info_list_sorted)
