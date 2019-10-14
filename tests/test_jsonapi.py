from libs.rest.format.jsonapi import parse_data


DATA = {
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

def test_json_api_parser():
    data = parse_data(DATA)
    print(data)
    input_keys = sorted(DATA["data"]["attributes"].keys())
    output_keys = sorted(data.keys())
    assert  all(key_output == key_input for key_output, key_input in zip(output_keys, input_keys))
    assert  all(data[key_output] == DATA["data"]["attributes"][key_input] for key_output, key_input in zip(output_keys, input_keys))