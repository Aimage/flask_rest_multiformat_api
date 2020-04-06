from flask_rest_multiformat_api.format.jsonapi import JsonApiFormater
from copy import deepcopy
import json
from flask_rest_multiformat_api.exceptions import ApiException
import pytest


@pytest.fixture
def jsonapi_formater():
    yield JsonApiFormater()


RIGHT_DATA = {
            "data":
                {
                  "attributes":
                            {
                              "type": 1,
                              "name": "place test",
                              "description": "descr test",
                              "map_link": "http://test.fr",
                              "is_private": 0
                             }
                }
            }
            

RIGHT_DATA2 = {
                  "data": {
                    "type": "photos",
                    "id": 1,
                    "attributes": {
                      "title": "Ember Hamster",
                      "src": "http://example.com/images/productivity.png"
                    },
                    "relationships": {
                      "photographer": {
                        "data": { "type": "people", "id": "9" }
                      }
                    }
                  }
                }
                

DATA_WITHOUT_DATA_KEY = {
                    "type": "photos",
                    "id": 1,
                    "attributes": {
                      "title": "Ember Hamster",
                      "src": "http://example.com/images/productivity.png"
                    },
                    "relationships": {
                      "photographer": {
                        "data": { "type": "people", "id": "9" }
                      }
                    }
                  }

RIGHT_DATA2_TXT = json.dumps(RIGHT_DATA2)
RIGHT_DATA_TXT = json.dumps(RIGHT_DATA)            
RIGHT_DATAS = """[{},{}]""".format(RIGHT_DATA_TXT, RIGHT_DATA2_TXT)
DATA_WITHOUT_DATA_KEY_TXT = json.dumps(DATA_WITHOUT_DATA_KEY)


def verify_data(data1, data2):
    for key, val in data1.items():
        assert data2.get(key) is not None
        assert data2.get(key) == data1.get(key)


def test_right_data(jsonapi_formater):
    result = jsonapi_formater.parse_data(RIGHT_DATA2_TXT)
    original_data = RIGHT_DATA2
    verify_data(original_data["data"]["attributes"], result) 


def test_right_datas(jsonapi_formater):
    result = jsonapi_formater.parse_data(RIGHT_DATAS)
    original_data = json.loads(RIGHT_DATAS)
    for data, origin in zip(result, original_data):
        verify_data(origin["data"]["attributes"], data) 


def test_data_without_data_key(jsonapi_formater):
    try:
        result = jsonapi_formater.parse_data(DATA_WITHOUT_DATA_KEY_TXT)
    except ValueError as e:
        message = e.messages
    assert message == "Missing \"data\" key"