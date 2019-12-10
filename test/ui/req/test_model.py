import unittest

from multiply_ui.ui.req.model import InputRequest, ProcessingRequest, InputIdentifiers


class RequestModelTest(unittest.TestCase):

    def test_input_request(self):
        input_request = InputRequest(dict(name='bibo',
                                          bbox='10.2,51.2,11.3,53.6',
                                          timeRange=['2018-07-06', '2018-07-20'],
                                          timeStep=4,
                                          timeStepUnit='days',
                                          spatialResolution=20,
                                          inputTypes=['S2_L1C'],
                                          forwardModels=[
                                              dict(name='s1_sail',
                                                   type='kafka',
                                                   modelDataType='Sentinel-1',
                                                   requiredPriors=['rgwf6', 'fg6'],
                                                   outputParameters=['LAI'])],
                                          userPriors=[
                                              dict(name='LAI',
                                                   mu=0.2,
                                                   unc=0.01),
                                              dict(name='ALA',
                                                   mu=1.3),
                                              dict(name='fzxh',
                                                   unc=0.01)]
                                          )
                                     )

        self.assertEqual('bibo', input_request.name)
        self.assertEqual((10.2, 51.2, 11.3, 53.6), input_request.bbox)
        self.assertEqual(('2018-07-06', '2018-07-20'), input_request.time_range)
        self.assertEqual(4, input_request.time_step)
        self.assertEqual('days', input_request.time_step_unit)
        self.assertEqual(20, input_request.spatialResolution)
        self.assertEqual(['S2_L1C'], input_request.input_types)
        self.assertEqual('s1_sail', input_request.forward_models[0]['name'])
        self.assertEqual('kafka', input_request.forward_models[0]['type'])
        self.assertEqual('Sentinel-1', input_request.forward_models[0]['modelDataType'])
        self.assertEqual('rgwf6', input_request.forward_models[0]['requiredPriors'][0])
        self.assertEqual('fg6', input_request.forward_models[0]['requiredPriors'][1])
        self.assertEqual('LAI', input_request.forward_models[0]['outputParameters'][0])
        self.assertEqual(3, len(input_request.user_priors))
        self.assertEqual('LAI', input_request.user_priors[0]['name'])
        self.assertEqual(0.2, input_request.user_priors[0]['mu'])
        self.assertEqual(0.01, input_request.user_priors[0]['unc'])
        self.assertEqual('ALA', input_request.user_priors[1]['name'])
        self.assertEqual(1.3, input_request.user_priors[1]['mu'])
        self.assertEqual('fzxh', input_request.user_priors[2]['name'])
        self.assertEqual(0.01, input_request.user_priors[2]['unc'])

        self.assertIsNotNone(input_request._repr_html_())

    def test_processing_request(self):
        input_request = ProcessingRequest(dict(name='bibo',
                                               bbox='10.2,51.2,11.3,53.6',
                                               timeRange=['2018-07-06', '2018-07-20'],
                                               timeStep=4,
                                               timeStepUnit='days',
                                               spatialResolution=20,
                                               inputTypes=['S2_L1C'],
                                               forwardModels=[dict(
                                                   name='s1_sail',
                                                   type='kafka',
                                                   modelDataType='Sentinel-1',
                                                   requiredPriors=['rgwf6', 'fg6'],
                                                   outputParameters=['LAI'],
                                               )],
                                               userPriors=[
                                                   dict(name='LAI',
                                                        mu=0.2,
                                                        unc=0.01),
                                                   dict(name='ALA',
                                                        mu=1.3),
                                                   dict(name='fzxh',
                                                        unc=0.01)],
                                               inputIdentifiers={'S2_L1C': ['IID1', 'IID2', 'IID3']}))

        self.assertEqual('bibo', input_request.name)
        self.assertEqual((10.2, 51.2, 11.3, 53.6), input_request.bbox)
        self.assertEqual(('2018-07-06', '2018-07-20'), input_request.time_range)
        self.assertEqual(4, input_request.time_step)
        self.assertEqual('days', input_request.time_step_unit)
        self.assertEqual(20, input_request.spatialResolution)
        self.assertEqual(['S2_L1C'], input_request.input_types)
        self.assertEqual('s1_sail', input_request.forward_models[0]['name'])
        self.assertEqual('kafka', input_request.forward_models[0]['type'])
        self.assertEqual('Sentinel-1', input_request.forward_models[0]['modelDataType'])
        self.assertEqual('rgwf6', input_request.forward_models[0]['requiredPriors'][0])
        self.assertEqual('fg6', input_request.forward_models[0]['requiredPriors'][1])
        self.assertEqual('LAI', input_request.forward_models[0]['outputParameters'][0])
        self.assertEqual(3, len(input_request.user_priors))
        self.assertEqual('LAI', input_request.user_priors[0]['name'])
        self.assertEqual(0.2, input_request.user_priors[0]['mu'])
        self.assertEqual(0.01, input_request.user_priors[0]['unc'])
        self.assertEqual('ALA', input_request.user_priors[1]['name'])
        self.assertEqual(1.3, input_request.user_priors[1]['mu'])
        self.assertEqual('fzxh', input_request.user_priors[2]['name'])
        self.assertEqual(0.01, input_request.user_priors[2]['unc'])
        self.assertIsInstance(input_request.inputs, InputIdentifiers)
        self.assertIsNotNone(input_request._repr_html_())

    def test_input_identifiers(self):
        input_identifiers = InputIdentifiers({'S2_L1C': ['IID1', 'IID2', 'IID3']})

        self.assertIsNotNone(input_identifiers._repr_html_())
