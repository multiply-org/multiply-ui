import datetime
from typing import List

import ipywidgets as widgets

from multiply_ui.ui.req.model import InputRequest, ProcessingRequest
from .api import fetch_inputs
from ..params.model import ProcessingParameters


def sel_params_form(processing_parameters: ProcessingParameters, fetch_inputs_func=None):
    fetch_inputs_func = fetch_inputs_func or fetch_inputs

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

    spatial_resolution = widgets.Dropdown(
        options=['10', '20', '60', '300'],
        value='60',
        disabled=False,
    )

    time_steps = widgets.Dropdown(
        options=['1d', '8d', '10d', 'cal. week', 'cal. month'],
        value='8d',
        disabled=False,
    )

    # output = widgets.HTML(layout=dict(border='2px solid lightgray', padding='0.5em'))
    output = widgets.HTML()

    # noinspection PyUnusedLocal
    def handle_new_button_clicked(*args, **kwargs):
        # TODO: infer input types
        input_types = ['S2_L1C']
        x1, x2 = lon_range.value
        y1, y2 = lat_range.value

        try:
            inputs_request = InputRequest(dict(
                name=request_name.value,
                timeRange=[start_date.value, end_date.value],
                bbox=f'{x1},{y1},{x2},{y2}',
                inputTypes=input_types,
            ))
            output.value = f'<h2>{str(inputs_request)}</h2>'
        except Exception as e:
            output.value = f'<h2>{str(e)}</h2>'
            return

        def handle_processing_request(processing_request: ProcessingRequest):
            #globals()['req'] = processing_request
            import sys
            module = sys.modules[__name__]
            setattr(module, 'req', processing_request)

            # TODO: insert new cell that contains a NB variable whose value is processing_request
            # TODO: users can later call the GUI with that object to edit it

            # noinspection PyProtectedMember
            try:
                output.value = processing_request._repr_html_()
            except Exception as e:
                output.value = f'<h2>{str(e)}</h2>'

        fetch_inputs_func(inputs_request, apply_func=handle_processing_request)

    new_button = widgets.Button(description="New Request", icon="search")
    new_button.on_click(handle_new_button_clicked)
    form_items = [
        widgets.Box([widgets.Label(value='Output variables')], layout=form_item_layout),
        widgets.Box([variables_box], layout=var_checks_layout),
        widgets.Box([widgets.Label(value='Forward models')], layout=form_item_layout),
        widgets.Box([forward_models_box], layout=var_checks_layout),
        widgets.Box([widgets.Label(value='Start date'), start_date], layout=form_item_layout),
        widgets.Box([widgets.Label(value='End date'), end_date], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Time steps'), time_steps], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Longitude'), lon_range], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Latitude'), lat_range], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Resolution (m)'), spatial_resolution], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Request name'), request_name], layout=form_item_layout),
        widgets.Box([widgets.Label(value=''), new_button], layout=form_item_layout),
        widgets.Box([output], layout=form_item_layout),
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
    # noinspection PyUnusedLocal
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
