import json
from flask import make_response
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


def build_error_data(message, title="", source="", status=400):
    error = {"detail": message,
             "source": source,
             "status": status,
             "title": title
             }
    return error


def format_response(response_dict):
    return json.dumps(response_dict)


def build_error_response(errors):
    code = errors[0].code if len(errors) == 1 else 422
    errors_dict = [build_error_data(error.detail, error.title, error.source, error.status)
                   for error in errors
                   ]
    errors_response = {"errors": errors_dict}
    error_response = format_response(errors_response)
    response = create_response(error_response, code)
    return response


def create_response(response_content, code=200):
    response = make_response(response_content, code)
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response