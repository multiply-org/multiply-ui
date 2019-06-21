import json
import os
import unittest

import pkg_resources

from multiply_ui.ui.job.model import Job, Tasks

RAW_DATA = json.loads(pkg_resources.resource_string("multiply_ui", "server/resources/processing-parameters.json"))


class JobModelTest(unittest.TestCase):

    def test_instantiation_from_raw_data(self):
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'test_data', 'example_job.json')) as fp:
            json_text = fp.read()
            parameters = json.loads(json_text)
            job = Job(parameters)
            self.assertIsNotNone(job)
            self.assertEqual('7816-23af-e273', job.id)
            self.assertEqual('My job #2', job.name)
            self.assertEqual(15, job.progress)
            self.assertEqual('running', job.status)
            self.assertIsInstance(job.tasks, Tasks)
            self.assertEqual(['Fetching static Data', 'Collecting Data from 2017-06-01 to 2017-06-10',
                              'Collecting Data from 2017-06-11 to 2017-06-20',
                              'Performing atmospheric correction on Data from 2017-06-01 to 2017-06-10',
                              'Performing atmospheric correction on Data from 2017-06-11 to 2017-06-20',
                              "Retrieving prior information from 2017-06-01 to 2017-06-10",
                              "Retrieving prior information from 2017-06-11 to 2017-06-20",
                              "Inferring variables from 2017-06-01 to 2017-06-10",
                              "Inferring variables from 2017-06-11 to 2017-06-20"],
                             job.tasks.names)
            self.assertIsNotNone(job._repr_html_())
            self.assertIsNotNone(job.tasks._repr_html_())
