import json
from flask import make_response
from flask_rest_multiformat_api.errors import InvalidDataformatError
from flask_rest_multiformat_api.exceptions import ApiException


class SipleJsonFormater():
    
    def build_data_dict(self, orm_obj__dict, type='', **kwargs):
        return orm_obj__dict
    
    def parse(self, data):
        data = data.get("data")
        if data is None: 
            detail = 'Missing "data" key'
            error = InvalidDataformatError(__name__, detail)
            raise ApiException([error], code=400)
        return data

    def parse_data(self, data):
        parsed_data = None
        try:
            data = json.loads(data)
        except:
            error = InvalidDataformatError(__name__)
            raise ApiException([error], code=400)
        if isinstance(data, list):
            parsed_data = []
            for data_to_parse in data:
                data = self.parse(data_to_parse)
                parsed_data.append(data)
        else:
            parsed_data = self.parse(data)
        return parsed_data

    def build_error_data(self, message, title="", source="", status=400):
        error = {"detail": message,
                 "source": source,
                 "status": status,
                 "title": title
                 }
        return error

    def format_response(self, response_dict):
        return json.dumps(response_dict)

    def build_error_response(self, errors):
        code = errors[0].code if len(errors) == 1 else 422
        errors_dict = [self.build_error_data(error.detail, error.title, error.source, error.status)
                       for error in errors
                       ]
        errors_response = {"errors": errors_dict}
        error_response = self.format_response(errors_response)
        response = self.create_response(error_response, code)
        return response

    def create_response(self, response_content, code=200):
        response = make_response(response_content, code)
        response.headers['Content-Type'] = 'application/vnd.api+json'
        return response
