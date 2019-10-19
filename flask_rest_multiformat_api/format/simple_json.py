import json
from flask_rest_multiformat_api.errors import InvalidDataformatError
from flask_rest_multiformat_api.exceptions import ApiException


def build_data_dict(orm_obj__dict, type=''):
    return orm_obj__dict


def parse(data):
    data = data.get("data")
    if data is None: 
        detail = 'Missing "data" key'
        error = InvalidDataformatError(__name__, detail)
        raise ApiException([error], code=400)
    return data


def parse_data(data):
    parsed_data = None
    try:
        data = json.loads(data)
    except:
        error = InvalidDataformatError(__name__)
        raise ApiException([error], code=400)
    if isinstance(data, list):
        parsed_data = []
        for data_to_parse in data:
            data = parse(data_to_parse)
            parsed_data.append(data)
    else:
        parsed_data = parse(data)
    return parsed_data


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
