import json


def build_data_dict(orm_obj__dict, type=''):
    return orm_obj__dict


def parse_data(data):
    data = data.get("data")
    if data is None: 
        raise ValueError("Missing \"data\" key")
    return data


def build_error_data(message, source="", code=400):
    error= {"message" : message,
            "code": code, 
            }
    return error


def format_response(response_dict):
    return json.dumps(response_dict)


def build_error_response(message, source="", code=400):
    response_dict = build_error_data(message, source, code)
    error_response = format_response(response_dict)
    return error_response
