import datetime
from typing import List, Dict

import ipywidgets as widgets

from ..ui.procparams import ProcessingParameters
from ..util.callapi import call_api

URL_BASE = "http://localhost:9090/"

GET_INPUTS_URL = URL_BASE + "multiply/api/processing/inputs"


def sel_params_form(processing_parameters: ProcessingParameters):
    form_item_layout = widgets.Layout(
        display='flex',
        flex_flow='row',
        justify_content='space-between',
    )
    var_checks_layout = widgets.Layout(
        display='flex',
        flex_flow='row',
        justify_content='center',
    )

    variables_box = _get_checkbox_list(processing_parameters.variables.ids)
    forward_models_box = _get_checkbox_list(processing_parameters.forward_models.ids)

    # output_variables =

    request_name = widgets.Text()

    start_date = widgets.DatePicker(value=datetime.datetime(year=2010, month=1, day=1))
    end_date = widgets.DatePicker(value=datetime.datetime(year=2019, month=1, day=1))

    def format_angle(a):
        if a < 0:
            return f" {a} "
        if a > 0:
            return f" +{a} "
        return " 0 "

    lon_range = widgets.SelectionRangeSlider(
        options=[(format_angle(i - 180), i) for i in range(0, 361)],
        index=(0, 360)
    )

    lat_range = widgets.SelectionRangeSlider(
        options=[(format_angle(i - 90), i) for i in range(0, 181)],
        index=(0, 180)
    )

    # noinspection PyUnusedLocal
    def handle_new_button_clicked(*args, **kwargs):
        print("Heeelllooooooo!!!!" * 10)
        inputs_request = dict(
            requestName=request_name.value,
            timeRange=[start_date.value, end_date.value],
            regionBox=[lon_range.value[0], lat_range.value[0], lon_range.value[1], lat_range.value[1]]
        )

        def apply_func(inputs_response: Dict):
            # TODO: merge inputs_response with variables, fmodels, etc to create a processing request
            # TODO: insert new cell that contains a NB variable whose value is of type ProcessingRequest
            #  that can render HTML
            # TODO: Users can later call the GUI with that object to edit it
            print(inputs_response)

        call_api(GET_INPUTS_URL, apply_func=apply_func)

    new_button = widgets.Button(description="New", icon="search")
    new_button.on_click(handle_new_button_clicked)
    form_items = [
        widgets.Box([widgets.Label(value='Output variables')], layout=form_item_layout),
        widgets.Box([variables_box], layout=var_checks_layout),
        widgets.Box([widgets.Label(value='Forward models')], layout=form_item_layout),
        widgets.Box([forward_models_box], layout=var_checks_layout),
        widgets.Box([widgets.Label(value='Start date'), start_date], layout=form_item_layout),
        widgets.Box([widgets.Label(value='End date'), end_date], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Longitude'), lon_range], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Latitude'), lat_range], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Request name'), request_name], layout=form_item_layout),
        widgets.Box([widgets.Label(value=''), new_button], layout=form_item_layout),
    ]

    form = widgets.Box(form_items, layout=widgets.Layout(
        display='flex',
        flex_flow='column',
        border='solid 1px lightgray',
        align_items='stretch',
        width='50%'
    ))

    return form


def _get_checkbox_list(ids: List[str]) -> widgets.HBox:
    num_cols = 4
    v_box_item_lists = [[] for i in range(num_cols)]
    index = 0
    for var_id in ids:
        col = index % num_cols
        v_box_item_lists[col].append(widgets.Checkbox(
            value=False,
            description=var_id,
            disabled=False
        ))
        index += 1

    v_boxes = []
    for v_box_item_list in v_box_item_lists:
        v_boxes.append(widgets.VBox(v_box_item_list))
    return widgets.HBox(v_boxes)
