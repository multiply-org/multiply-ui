import pkg_resources
import multiply_ui.server.controller as controller
import json
import multiply_ui.server.context as context


def test_get_parameters():
    parameters = controller.get_parameters(None)
    assert 1 == len(parameters["inputTypes"])
    assert parameters["inputTypes"][0]["name"] == "Sentinel-2 MSI L1C"


def test_get_request():
    json_text = pkg_resources.resource_string("test", "test_data/example_request_parameters.json")
    parameters = json.loads(json_text)
    request = controller.get_request(context.ServiceContext(), parameters)
    assert "request-1" == request["request"]["id"]
    assert 50 == len(request["request"]["productIdentifiers"]["S2_L1C"])


