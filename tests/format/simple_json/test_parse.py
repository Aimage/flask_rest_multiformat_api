from flask_rest_multiformat_api.format import simple_json
from flask_rest_multiformat_api.exceptions import ApiException
from flask_rest_multiformat_api.errors import InvalidDataformatError
import json
from copy import deepcopy

RIGHT_DATA = {
                "data":
                    {
                        "id": 1,
                        "type": 1,
                        "name": "place test",
                        "description": "descr test",
                        "map_link": "http://test.fr",
                        "is_private": 0
                    }
                }
RIGHT_DATA_TXT = json.dumps(RIGHT_DATA) 


def test_parse_right_data():
    result = simple_json.parse_data(RIGHT_DATA_TXT)
    assert result == RIGHT_DATA["data"]
    
    
def test_parse_wrong_format_data():
    wrong_data = "{} {}".format(RIGHT_DATA_TXT, "hehehe, hihihi")
    try:
        result = simple_json.parse_data(wrong_data)
    except ApiException as e:
        assert isinstance(e.errors[0], InvalidDataformatError)


def test_parse_missing_data_key():
    wrong_data = deepcopy(RIGHT_DATA)
    del(wrong_data["data"])
    try:
        result = simple_json.parse_data(json.dumps(wrong_data))
    except ApiException as e:
        assert isinstance(e.errors[0], InvalidDataformatError), "Not invalid data format error"        
        assert e.code == 400, "Code not equal to 400"
        assert e.errors[0].detail == 'Missing "data" key', "Detail error not equal"
