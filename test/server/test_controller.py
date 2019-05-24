import json
import os
import unittest

from multiply_ui.server import controller


class ControllerTest(unittest.TestCase):

    def test_get_parameters(self):
        parameters = controller.get_parameters(None)
        self.assertEqual(1, len(parameters["inputTypes"]))
        self.assertEqual(parameters["inputTypes"][0]["name"], "Sentinel-2 MSI L1C")

    @unittest.skipIf(os.environ.get('MULTIPLY_DISABLE_WEB_TESTS') == '1', 'MULTIPLY_DISABLE_WEB_TESTS = 1')
    def test_get_inputs(self):
        from multiply_ui.server import context
        with open(os.path.join(os.path.dirname(__file__), '..', 'test_data', 'example_request_parameters.json')) as fp:
            json_text = fp.read()
            parameters = json.loads(json_text)
            request = controller.get_inputs(context.ServiceContext(), parameters)
            self.assertEqual(50, len(request["productIdentifiers"]["S2_L1C"]))


if __name__ == '__main__':
    unittest.main()
