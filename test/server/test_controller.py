import multiply_ui.server.controller as controller
import json
import multiply_ui.server.context as context
import unittest


class ControllerTest(unittest.TestCase):

    def test_get_parameters(self):
        parameters = controller.get_parameters(None)
        self.assertEqual(1, len(parameters["inputTypes"]))
        self.assertEqual(parameters["inputTypes"][0]["name"], "Sentinel-2 MSI L1C")

    def test_get_inputs(self):
        with open("test/test_data/example_request_parameters.json") as f:
            json_text = f.read()
            parameters = json.loads(json_text)
            request = controller.get_inputs(context.ServiceContext(), parameters)
            self.assertEqual(50, len(request["productIdentifiers"]["S2_L1C"]))


if __name__ == '__main__':
    unittest.main()
