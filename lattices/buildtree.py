from utils.fileio import load_json


def switch_dict(_lattice):
    data_type_dict = load_json('lattices/datatype_dictionary.json')
    purpose_dict = load_json('lattices/purpose_dictionary.json')

    _data_type, _purpose = _lattice['dataType'], _lattice['purpose']
    datatype_gen = generate(_data_type, data_type_dict)
    purpose_gen = generate(_purpose, purpose_dict)
    return {"dataType": datatype_gen, "purpose": purpose_gen}


def generate(_datatype, datatype_dictionary, datatype_gen=None, prefix=None):
    if datatype_gen is None:
        datatype_gen = dict()
    if prefix is None:
        prefix = ""
    for key in _datatype.keys():
        prefix_son = key if prefix == "" else (prefix + '/' + key)
        if isinstance(_datatype[key], dict):
            datatype_gen = generate(_datatype[key], datatype_dictionary, datatype_gen, prefix_son)
        elif len(_datatype[key]) == 0:
            if key in datatype_dictionary.keys():
                datatype_gen[key] = {"path": prefix_son, "abbr": datatype_dictionary[key]["abbr"]}
            else:
                datatype_gen[key] = {"path": prefix_son, "abbr": [key]}
        else:
            for _type in _datatype[key]:
                prefix_grandson = prefix_son + '/' + _type
                if _type in datatype_dictionary.keys():
                    datatype_gen[_type] = {"path": prefix_grandson, "abbr": datatype_dictionary[_type]["abbr"]}
                else:
                    datatype_gen[_type] = {"path": prefix_grandson, "abbr": [_type]}
    return datatype_gen


if __name__ == '__main__':
    data_type = load_json('datatype.json')
    purpose = load_json('purpose.json')
    lattice = {'dataType': data_type, 'purpose': purpose}
    switch_dict(lattice)


