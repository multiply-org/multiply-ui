import json
import unittest

import pkg_resources

from multiply_ui.ui.procparams import ProcessingParameters, Variables, ForwardModels

RAW_DATA = json.loads(pkg_resources.resource_string("multiply_ui", "server/resources/processing-parameters.json"))


class ProcessingParametersTest(unittest.TestCase):

    def test_instantiation_from_raw_data(self):
        proc_param = ProcessingParameters(RAW_DATA)
        self.assertIsNotNone(proc_param)
        self.assertIsInstance(proc_param.variables, Variables)
        self.assertEqual(['lai', 'cab', 'cb', 'car', 'cw', 'cdm', 'n', 'ala', 'bsoil', 'psoil', 'GeoCBI', 'cm'],
                         proc_param.variables.ids)

        self.assertIsInstance(proc_param.forward_models, ForwardModels)
        self.assertEqual(['s2_prosail'],
                         proc_param.forward_models.ids)
