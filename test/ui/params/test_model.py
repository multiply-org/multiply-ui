import json
import unittest

import pkg_resources

from multiply_ui.ui.params.model import ProcessingParameters, Variables, ForwardModels, InputTypes, PostProcessors

RAW_DATA = json.loads(pkg_resources.resource_string("multiply_ui", "server/resources/processing-parameters.json"))


class ProcessingParametersTest(unittest.TestCase):

    def test_instantiation_from_raw_data(self):
        proc_params = ProcessingParameters(RAW_DATA)

        self.assertIsInstance(proc_params.variables, Variables)
        self.assertEqual(['lai', 'cab', 'cb', 'car', 'cw', 'cdm', 'n', 'ala', 'bsoil', 'psoil'],
                         proc_params.variables.ids)
        self.assertIsNotNone(proc_params.variables._repr_html_())

        self.assertIsInstance(proc_params.forward_models, ForwardModels)
        self.assertEqual(['s2_prosail'],
                         proc_params.forward_models.ids)
        self.assertIsNotNone(proc_params.forward_models._repr_html_())

        self.assertIsInstance(proc_params.input_types, InputTypes)
        self.assertEqual(['S2_L1C'],
                         proc_params.input_types.ids)
        self.assertIsInstance(proc_params.input_types, InputTypes)
        self.assertIsNotNone(proc_params.input_types._repr_html_())

        self.assertIsInstance(proc_params.post_processors, PostProcessors)
        self.assertEqual(['MyFirstPostProcessor', 'MySecondPostProcessor'],
                         proc_params.post_processors.names)
        self.assertIsNotNone(proc_params.post_processors._repr_html_())

        self.assertIsInstance(proc_params.indicators, Variables)
        self.assertEqual(['rdshfc', 'hzrgnbhznt', 'jdfgbzt'],
                         proc_params.indicators.ids)
        self.assertIsNotNone(proc_params.indicators._repr_html_())
