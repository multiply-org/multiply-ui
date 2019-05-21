import json


class Controller(object):

    def get_parameters(self):
        with open('test/test_data/example_parameters.json') as f:
            return json.load(f)