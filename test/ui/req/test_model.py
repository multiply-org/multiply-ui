import unittest

from multiply_ui.ui.req.model import InputRequest, ProcessingRequest, InputIdentifiers


class RequestModelTest(unittest.TestCase):

    def test_input_request(self):
        input_request = InputRequest(dict(name='bibo',
                                          bbox='10.2,51.2,11.3,53.6',
                                          timeRange=['2018-07-06', '2018-07-20'],
                                          inputTypes=['S2_L1C']))

        self.assertEqual('bibo', input_request.name)
        self.assertEqual((10.2, 51.2, 11.3, 53.6), input_request.bbox)
        self.assertEqual(('2018-07-06', '2018-07-20'), input_request.time_range)
        self.assertEqual(['S2_L1C'], input_request.input_types)
        self.assertIsNotNone(input_request._repr_html_())

    def test_processing_request(self):
        input_request = ProcessingRequest(dict(name='bibo',
                                               bbox='10.2,51.2,11.3,53.6',
                                               timeRange=['2018-07-06', '2018-07-20'],
                                               inputTypes=['S2_L1C'],
                                               inputIdentifiers={'S2_L1C': ['IID1', 'IID2', 'IID3']}))

        self.assertEqual('bibo', input_request.name)
        self.assertEqual((10.2, 51.2, 11.3, 53.6), input_request.bbox)
        self.assertEqual(('2018-07-06', '2018-07-20'), input_request.time_range)
        self.assertEqual(['S2_L1C'], input_request.input_types)
        self.assertIsInstance(input_request.input_identifiers, InputIdentifiers)
        self.assertIsNotNone(input_request._repr_html_())

    def test_input_identifiers(self):
        input_identifiers = InputIdentifiers({'S2_L1C': ['IID1', 'IID2', 'IID3']})

        self.assertIsNotNone(input_identifiers._repr_html_())
