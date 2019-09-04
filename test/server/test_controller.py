import glob
import json
import multiply_ui.server.controller as controller
import multiply_ui.server.context as context
import os
import shutil
import time
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
        # copying files as they are changed during processing
        if not os.path.exists('./test_data/test_scripts_2'):
            os.mkdir('./test_data/test_scripts_2')
        scripts = glob.glob('./test_data/test_scripts/*.py')
        for script in scripts:
            shutil.copy(script, './test_data/test_scripts_2')
        with open("./test_data/example_request_parameters_2.json") as f:
            json_text = f.read()
            parameters = json.loads(json_text)
            service_context = context.ServiceContext()
            working_dir = './test_data/multiply'
            if not os.path.exists(working_dir):
                os.mkdir(working_dir)
            service_context.set_working_dir(working_dir)
            service_context.add_workflows_path('./test_data/test_workflows')
            service_context.add_scripts_path('./test_data/test_scripts_2')
            try:
                job = controller.submit_request(service_context, parameters)
                self.assertIsNotNone(job)
                self.assertTrue('name' in job.keys())
                self.assertEqual('Model-1_Baikalsee_LAI_2018', job['id'])
                self.assertEqual('Model-1 Baikalsee LAI 2018', job['name'])
            finally:
                time.sleep(5)
                shutil.rmtree(working_dir)
                shutil.rmtree('./test_data/test_scripts_2')


if __name__ == '__main__':
    unittest.main()
