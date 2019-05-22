import json
import pkg_resources


def get_parameters(ctx):
    json_text = pkg_resources.resource_string(__name__, "resources/processing-parameters.json")
    return json.loads(json_text)


def get_inputs(ctx, parameters):
    time_range = parameters["timeRange"]
    (minLon, minLat, maxLon, maxLat) = parameters["bbox"].split(",")
    region_wkt = "POLYGON(({} {},{} {},{} {},{} {},{} {}))".format(minLon, minLat, maxLon, minLat, maxLon, maxLat,
                                                                   minLon, maxLat, minLon, minLat)
    input_types = parameters["inputTypes"]
    parameters["productIdentifiers"] = {}
    for input_type in input_types:
        data_set_meta_infos = ctx.data_access_component.query(region_wkt, time_range[0], time_range[1], input_type)
        parameters["productIdentifiers"][input_type] = [entry._identifier for entry in data_set_meta_infos]
    return parameters
