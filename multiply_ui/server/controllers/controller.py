import json


class Controller(object):

    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Controller.__instance is None:
            Controller()
        return Controller.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Controller.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Controller.__instance = self

    def get_parameters(self):
        with open('variables-test.json') as f:
            return json.load(f)