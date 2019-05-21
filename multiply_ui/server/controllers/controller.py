import json
import pkg_resources

def get_parameters(ctx):
    json_text = pkg_resources.resource_string("multiply_ui", "server/resources/processing-parameters.json")
    return json.loads(json_text)
