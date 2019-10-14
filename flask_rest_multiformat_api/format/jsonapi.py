from copy import deepcopy
import json


DATA_BASE_DICT = {"type": "",
                  "attributes": {},
                  "id": 0,
                  "links": {},
                  }


def build_data_dict(orm_obj__dict, type='', links={}):
    def build_data(_orm_obj_dict):
        data_dict = deepcopy(DATA_BASE_DICT)
        link_dict = deepcopy(links)
        data_dict["attributes"] = _orm_obj_dict
        data_dict["id"] = _orm_obj_dict['id']
        data_dict["type"] = type
        link_dict['self'] = "{}{}".format(link_dict['self'], _orm_obj_dict['id'])
        data_dict["links"] = link_dict
        return data_dict
    if isinstance(orm_obj__dict, list):
        data_dict = [build_data(_orm_obj_dict) for _orm_obj_dict in orm_obj__dict]
    else:
        data_dict = build_data(orm_obj__dict)
    return data_dict


def parse_data(data):
    data = data.get("data")
    if data is None:
        raise ValueError("Missing \"data\" key")
    if data.get("attributes") is None:
        raise ValueError('Missing "attributes" key in data dict')
    new_data = data["attributes"]
    if data.get('id'):
        new_data['id'] = data['id']
    return new_data


def build_error_data(message, title="", source="", code=400):
    error = {"detail": message,
             "source": source,
             "status": code,
             "title": title
             }
    return error


def format_response(response_dict):
    return json.dumps(response_dict)


def build_error_response(detail, title="", source="", code=400):
    response_dict = build_error_data(detail, source, code)
    error_response = format_response(response_dict)
    return error_response
