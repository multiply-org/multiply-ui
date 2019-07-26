import multiply_ui.server.controller as controller
import json
import multiply_ui.server.context as context
import os
import shutil
import unittest


class ControllerTest(unittest.TestCase):

    def test_get_parameters(self):
        parameters = controller.get_parameters(None)
        self.assertEqual(1, len(parameters["inputTypes"]))
        self.assertEqual(parameters["inputTypes"][0]["name"], "Sentinel-2 MSI L1C")

    def test_get_inputs(self):
        with open("./test_data/example_request_parameters_1.json") as f:
            json_text = f.read()
            parameters = json.loads(json_text)
            request = controller.get_inputs(context.ServiceContext(), parameters)
            self.assertEqual(78, len(request["inputIdentifiers"]["S2_L1C"]))

    def test_submit_request(self):
        with open("./test_data/example_request_parameters_2.json") as f:
            json_text = f.read()
            parameters = json.loads(json_text)
            service_context = context.ServiceContext()
            working_dir = './test_data/multiply'
            if not os.path.exists(working_dir):
                os.mkdir(working_dir)
            service_context.set_working_dir(working_dir)
            service_context.add_workflows_path('./test_data/test_workflows')
            service_context.add_scripts_path('./test_data/test_scripts')
            try:
                job = controller.submit_request(service_context, parameters)
                self.assertIsNotNone(job)
                self.assertTrue('name' in job.keys())
                self.assertEqual('Model-1 Baikalsee LAI 2018', job['name'])
            finally:
                shutil.rmtree(working_dir)
                os.remove('Model-1 Baikalsee LAI 2018.report')
                os.remove('Model-1 Baikalsee LAI 2018.status')
                os.rmdir('log')
                os.rmdir('-p')


if __name__ == '__main__':
    unittest.main()
