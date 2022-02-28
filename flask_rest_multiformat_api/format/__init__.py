
from . import jsonapi
from flask_rest_multiformat_api.format import simple_json


DATA_FORMATER = {
                "jsonapi": jsonapi.JsonApiFormater,
                "simple_json": simple_json.SipleJsonFormater
                }
