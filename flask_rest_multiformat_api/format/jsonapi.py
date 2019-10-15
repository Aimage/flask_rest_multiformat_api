from copy import deepcopy
import json
from flask import make_response


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
        link_dict['self'] = "{}{}".format(link_dict['self'].split("<")[0], _orm_obj_dict['id'])
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


def build_error_data(message, title="", source="", status=400):
    error = {"detail": message,
             "source": source,
             "status": status,
             "title": title
             }
    return error


def format_response(response_dict):
    return json.dumps(response_dict)


def create_response(response_content, code=200):
    response = make_response(response_content, code)
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def build_error_response(errors):
    code = errors[0].code if len(errors) == 1 else 422
    errors_dict = [build_error_data(error.detail, error.title, error.source, error.status)
                   for error in errors
                   ]
    errors_response = {"errors": errors_dict}
    error_response = format_response(errors_response)
    response = create_response(error_response, code)
    return response

