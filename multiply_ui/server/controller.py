def get_parameters(ctx):
    input_type_dicts = ctx.get_available_input_types()
    variable_dicts = ctx.get_available_variables()
    forward_model_dicts = ctx.get_available_forward_models()
    parameters = {
        "inputTypes": input_type_dicts,
        "variables": variable_dicts,
        "forwardModels": forward_model_dicts
    }
    return parameters


def get_inputs(ctx, parameters):
    time_range = parameters["timeRange"]
    (minLon, minLat, maxLon, maxLat) = parameters["bbox"].split(",")
    region_wkt = "POLYGON(({} {},{} {},{} {},{} {},{} {}))".format(minLon, minLat, maxLon, minLat, maxLon, maxLat,
                                                                   minLon, maxLat, minLon, minLat)
    input_types = parameters["inputTypes"]
    parameters["inputIdentifiers"] = {}
    for input_type in input_types:
        data_set_meta_infos = ctx.data_access_component.query(region_wkt, time_range[0], time_range[1], input_type)
        parameters["inputIdentifiers"][input_type] = [entry._identifier for entry in data_set_meta_infos]
    return parameters


def set_earth_data_authentication(ctx, parameters):
    ctx.set_earth_data_authentication(parameters['user_name'], parameters['password'])


def set_mundi_authentication(ctx, parameters):
    ctx.set_mundi_authentication(parameters['access_key_id'], parameters['secret_access_key'])
