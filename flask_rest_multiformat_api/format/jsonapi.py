from copy import deepcopy
import json
from flask import make_response
from flask_rest_multiformat_api.errors import ApiError


DATA_BASE_DICT = {"type": "",
                  "attributes": {},
                  "id": 0,
                  "links": {},
                  }


class JsonApiFormater():
    
    def build_data_dict(self, orm_obj__dict, type='', links={}):
        def build_data(_orm_obj_dict):
            data_dict = deepcopy(DATA_BASE_DICT)
            link_dict = deepcopy(links)
            data_dict["attributes"] = _orm_obj_dict
            data_dict["id"] = _orm_obj_dict.pop('id')
            data_dict["type"] = type
            data_dict["links"] = link_dict
            return data_dict
        if isinstance(orm_obj__dict, list):
            data_dict = [build_data(_orm_obj_dict) for _orm_obj_dict in orm_obj__dict]
        else:
            data_dict = build_data(orm_obj__dict)
        return data_dict

    def parse(self, data):
        data = data.get("data")
        if data is None:
            raise ValueError("Missing \"data\" key")
        if data.get("attributes") is None:
            raise ValueError('Missing "attributes" key in data dict')
        new_data = data["attributes"]
        if data.get('id'):
            new_data['id'] = data['id']
        return new_data

    def parse_data(self, data):
        data = json.loads(data)
        parsed_data = None
        if isinstance(data, list):
            parsed_data = []
            for dat in data:
                parsed_data.append(self.parse(dat))
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

    def create_response(self, response_content, code=200):
        response = make_response(response_content, code)
        response.headers['Content-Type'] = 'application/vnd.api+json'
        return response

    def build_error_response(self, errors):
        code = errors[0].code if len(errors) == 1 else 422
        errors_dict = [self.build_error_data(error.detail, error.title, error.source, error.status)
                       for error in errors
                       ]
        errors_response = {"errors": errors_dict}
        error_response = self.format_response(errors_response)
        response = self.create_response(error_response, code)
        return response
