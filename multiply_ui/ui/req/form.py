from typing import List
from ipyleaflet import Map, basemaps, basemap_to_tiles, DrawControl, GeoJSON
from shapely.geometry import shape

import datetime
import IPython
import ipywidgets as widgets
import time

from .api import fetch_inputs
from .model import InputRequest, ProcessingRequest
from ..debug import get_debug_view
from ..job.api import submit_processing_request
from ..job.model import Job
from ..params.model import ProcessingParameters
from ...util.html import html_element, html_table

_NUM_REQUESTS = 0


def sel_params_form(processing_parameters: ProcessingParameters, identifier='identifier', name='name', mock=False):
    debug_view = get_debug_view()

    fetch_inputs_func = fetch_inputs
    if mock:
        @debug_view.capture(clear_output=True)
        def fetch_inputs_mock(input_request: InputRequest, apply_func):
            debug_view.value = ''
            time.sleep(2)
            input_identifiers = {input_type: [f'iid-{i}' for i in range(10)] for input_type in
                                 input_request.input_types}
            processing_request_data = input_request.as_dict()
            processing_request_data.update(dict(inputIdentifiers=input_identifiers))
            apply_func(ProcessingRequest(processing_request_data))

        fetch_inputs_func = fetch_inputs_mock

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

    variable_boxes = _get_checkbox_list(processing_parameters.variables.ids)
    forward_model_boxes = _get_checkbox_list(processing_parameters.forward_models.ids)

    def _get_selected_values(boxes: dict) -> List[str]:
        values = []
        for box in boxes.values():
            if box.value:
                values.append(box.description)
        return values

    def _get_selected_variables() -> List[str]:
        return _get_selected_values(variable_boxes)

    def _get_selected_forward_models() -> List[str]:
        return _get_selected_values(forward_model_boxes)

    def _handle_variable_selection(change: dict):
        output.value = html_element('h5',
                                        att=dict(style='color:red'),
                                        # value=f'{change.values()}')
                                        value=f'{change.keys()}')
        selected_variables = _get_selected_variables()
        # for forward_model_id in processing_parameters.forward_models.ids:
        #     if forward_model_boxes[forward_model_id]

    @debug_view.capture(clear_output=True)
    def _handle_forward_model_selection(change: dict):
        # output.value = html_element('h5',
        #                                 att=dict(style='color:red'),
        #                                 value=f'{change.values()}')
                                        # value=f'{change.keys()}')
        if change['name'] is 'layout':
            return
        owner = change['owner']
        selected_fm_id = owner.description
        selected_type = processing_parameters.forward_models.get(selected_fm_id).input_type
        layout = widgets.Layout(display='bold')
        owner.layout = layout
        # widgets.DescriptionStyle()
        # owner.layout = widgets.Layout(width='50%')
        # owner.style.button_color = 'lightblue'
        # output.value = html_element('h5',
        #                             att=dict(style='color:red'),
        #                             value=f'{owner.style.keys}')
        if change['new']['value'] == True:
            # output.value = html_element('h5',
            #                             att=dict(style='color:red'),
            #                             value='True detected')
            forward_model_ids = processing_parameters.forward_models.ids
            for id in forward_model_ids:
                # output.value = html_element('h5',
                #                             att=dict(style='color:red'),
                #                             value=f'{id}')
                if id == selected_fm_id:
                    continue
                if selected_type == processing_parameters.forward_models.get(id).input_type:
                    # output.value = html_element('h5',
                    #                             att=dict(style='color:red'),
                    #                             value='Input type match detected')
                    for child in forward_models_box.children:
                        # output.value = html_element('h5',
                        #                             att=dict(style='color:red'),
                        #                             value=f'{child.style.keys}')
                        if child.description == id:
                            # output.value = html_element('h5',
                            #                             att=dict(style='color:red'),
                            #                             value='Correct checkbox encountered')
                            child.value=False
                            child.disabled=True
                            break

    variables_box = _wrap_checkboxes_in_widget(variable_boxes.values(), _handle_variable_selection)
    forward_models_box = _wrap_checkboxes_in_widget(forward_model_boxes.values(), _handle_forward_model_selection)

    # output_variables =

    global _NUM_REQUESTS
    _NUM_REQUESTS += 1
    request_name = widgets.Text(name)
    python_var_name = widgets.Text(identifier)

    start_date = widgets.DatePicker(value=datetime.datetime(year=2010, month=1, day=1))
    end_date = widgets.DatePicker(value=datetime.datetime(year=2019, month=1, day=1))

    def format_angle(a):
        if a < 0:
            return f" {a} "
        if a > 0:
            return f" +{a} "
        return " 0 "

    map_background_layer = basemap_to_tiles(basemaps.OpenStreetMap.Mapnik)
    geometry_layer = GeoJSON()
    leaflet_map = Map(layers=(map_background_layer, geometry_layer), center=(39., -2.1), zoom=11)
    draw_control = DrawControl()
    draw_control.polyline = {}
    draw_control.polygon = {}
    draw_control.circlemarker = {}
    draw_control.rectangle = {'shapeOptions': {}}
    draw_control.edit = False
    draw_control.remove = False

    def _remove_previous_polygon(self, action, geo_json):
        self.clear()
        leaflet_map.remove_layer(leaflet_map.layers[1])
        geometry_layer = GeoJSON(data=geo_json['geometry'])
        leaflet_map.add_layer(geometry_layer)

    draw_control.on_draw(_remove_previous_polygon)
    leaflet_map.add_control(draw_control)

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

    def new_input_request():
        # TODO: infer input types from selected variables and forward models
        input_types = ['S2_L1C']

        roi_data = leaflet_map.layers[1].data
        if not roi_data:
            output.value = html_element('h5',
                                        att=dict(style='color:red'),
                                        value=f'Error: No region of Interest specified')
        roi = shape(roi_data)
        x1, y1, x2, y2 = roi.bounds

        return InputRequest(dict(
            name=request_name.value,
            timeRange=[start_date.value, end_date.value],
            bbox=f'{x1},{y1},{x2},{y2}',
            inputTypes=input_types,
        ))

    # noinspection PyUnusedLocal
    @debug_view.capture(clear_output=True)
    def handle_new_button_clicked(*args, **kwargs):
        req_var_name = python_var_name.value or 'req'
        if req_var_name and not req_var_name.isidentifier():
            output.value = html_element('h5',
                                        att=dict(style='color:red'),
                                        value=f'Error: invalid Python identifier: {req_var_name}')
            return

        inputs_request = new_input_request()

        def apply_func(processing_request: ProcessingRequest):

            input_identifiers = processing_request.inputs
            data_rows = []
            for input_type, input_ids in input_identifiers.as_dict().items():
                data_rows.append([input_type, len(input_ids)])

            result_html = html_table(data_rows, header_row=['Input Type', 'Number of inputs found'])

            # insert shall variable whose value is processing_request
            # users can later call the GUI with that object to edit it
            if req_var_name:
                shell = IPython.get_ipython()
                shell.push({req_var_name: processing_request}, interactive=True)
                var_name_html = html_element('p',
                                             value=f'Note: a new processing request has been '
                                             f'stored in variable <code>{req_var_name}</code>.')
                result_html = html_element('div',
                                           value=result_html + var_name_html)

            output.value = result_html

        output.value = html_element('h5', value='Fetching results...')
        fetch_inputs_func(inputs_request, apply_func=apply_func)

    # noinspection PyUnusedLocal
    @debug_view.capture(clear_output=True)
    def handle_submit_button_clicked(*args, **kwargs):
        req_var_name = python_var_name.value or 'job'
        if req_var_name and not req_var_name.isidentifier():
            output.value = html_element('h5',
                                        att=dict(style='color:red'),
                                        value=f'Error: invalid Python identifier: {req_var_name}')
            return

        inputs_request = new_input_request()

        def apply_func(job: Job):
            shell = IPython.get_ipython()
            shell.push({req_var_name: job}, interactive=True)
            result_html = html_element('p',
                                       value=f'Note: a new job is currently being executed and is '
                                       f'stored in variable <code>{req_var_name}</code>.')
            output.value = result_html

        output.value = html_element('h5', value='Submitting processing request...')
        submit_processing_request(inputs_request, apply_func=apply_func, mock=mock)

    # TODO: make GUI form look nice
    new_button = widgets.Button(description="New Request", icon="search")
    new_button.on_click(handle_new_button_clicked)
    submit_button = widgets.Button(description="Submit Request", icon="upload")
    submit_button.on_click(handle_submit_button_clicked)
    form_items = [
        widgets.Box([widgets.Label(value='Output variables')], layout=form_item_layout),
        widgets.Box([variables_box], layout=var_checks_layout),
        widgets.Box([widgets.Label(value='Forward models')], layout=form_item_layout),
        widgets.Box([forward_models_box], layout=var_checks_layout),
        widgets.Box([widgets.Label(value='Start date'), start_date], layout=form_item_layout),
        widgets.Box([widgets.Label(value='End date'), end_date], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Time steps'), time_steps], layout=form_item_layout),
        widgets.Box([widgets.Label(value="Region of Interest"), leaflet_map], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Resolution (m)'), spatial_resolution], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Request/job name'), request_name], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Python identifier'), python_var_name], layout=form_item_layout),
        widgets.Box([widgets.Label(value=''), widgets.Box([new_button, submit_button])], layout=form_item_layout),
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


def _get_checkbox_list(ids: List[str]) -> dict:
    checkboxes = {}
    for var_id in ids:
        checkbox = widgets.Checkbox(value=False, description=var_id, disabled=True
                                    # ,
                                    # layout=widgets.Layout(border='solid 1px lightgray')
                                    )

        checkboxes[var_id] = checkbox
    return checkboxes


def _wrap_checkboxes_in_widget(checkboxes: List[widgets.Checkbox], handle_selection) -> widgets.Widget:
    num_cols = 4
    # noinspection PyUnusedLocal
    v_box_item_lists = [[] for i in range(num_cols)]
    index = 0
    for checkbox in checkboxes:
        col = index % num_cols
        checkbox.observe(handle_selection)
        # noinspection PyTypeChecker
        v_box_item_lists[col].append(checkbox)
        index += 1
    v_boxes = []
    for v_box_item_list in v_box_item_lists:
        v_boxes.append(widgets.VBox(v_box_item_list))
    return widgets.HBox(v_boxes)
