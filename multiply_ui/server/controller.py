import json
import pkg_resources

def get_parameters(ctx):
    json_text = pkg_resources.resource_string("multiply_ui", "server/resources/processing-parameters.json")
    return json.loads(json_text)

def get_request(ctx, parameters):
        time_range = parameters["request"]["timeRange"]
        region_wkt = parameters["request"]["regionWKT"]
        input_types = set([parameter[2] for parameter in parameters["request"]["parameters"]])
        parameters["request"]["productIdentifiers"] = {}
        for input_type in input_types:
            data_set_meta_infos = ctx.data_access_component.query(region_wkt, time_range[0], time_range[1], input_type)
            parameters["request"]["productIdentifiers"][input_type] = [entry._identifier for entry in data_set_meta_infos]
        return parameters
