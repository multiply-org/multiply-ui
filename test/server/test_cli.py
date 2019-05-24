import unittest

import click.testing

from multiply_ui.server.cli import mui_server


class CliTest(unittest.TestCase):
    @classmethod
    def invoke_cli(cls, *args):
        runner = click.testing.CliRunner()
        return runner.invoke(mui_server, args, catch_exceptions=False)

    def test_help_option(self):
        result = self.invoke_cli('--help')
        self.assertEqual(0, result.exit_code)
        self.assertEqual(
            (
                'Usage: mui-server [OPTIONS]\n'
                '\n'
                '  Starts a service which exposes a RESTful API to the Multiply UI.\n'
                '\n'
                'Options:\n'
                '  -p, --port INTEGER  Set service port number. Defaults to 9090.\n'
                '  -a, --address TEXT  Set service IP address. Defaults to "0.0.0.0".\n'
                '  --help              Show this message and exit.\n'
            ),
            result.stdout)
