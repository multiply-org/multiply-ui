from typing import List
from ipyleaflet import Map, basemaps, basemap_to_tiles, DrawControl, GeoJSON
from shapely.geometry import shape

import datetime
import IPython
import ipywidgets as widgets
import time

from .api import fetch_inputs
from .model import InputRequest, ProcessingRequest
from ..checkbox_widget import LabeledCheckbox
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

    variable_boxes_dict = _get_checkboxes_dict(processing_parameters.variables.ids)
    forward_model_boxes_dict = _get_checkboxes_dict(processing_parameters.forward_models.ids)
    request_validation = widgets.HTML(value=html_element('h5',
                                        att=dict(style='color:red'),
                                        value='No variable or forward model selected'))
    available_forward_models_per_type = {}
    forward_models_per_variable = {}
    for fm_id in processing_parameters.forward_models.ids:
        fm = processing_parameters.forward_models.get(fm_id)
        if not fm.input_type in available_forward_models_per_type:
            available_forward_models_per_type[fm.input_type] = []
        available_forward_models_per_type[fm.input_type].append(fm_id)
        for variable in fm.variables:
            if not variable in forward_models_per_variable:
                forward_models_per_variable[variable] = []
            forward_models_per_variable[variable].append(fm_id)
    selected_forward_models = []
    selected_variables = []
    selected_forward_models_per_type = {}
    for it in processing_parameters.input_types.ids:
        selected_forward_models_per_type[it] = []

    def _fm_variables(fm_id: str):
        return processing_parameters.forward_models.get(fm_id).variables

    def _fm_input_type(fm_id: str):
        return processing_parameters.forward_models.get(fm_id).input_type

    def _recommend(id: str):
        if id in processing_parameters.variables.ids:
            _recommend_box(variable_boxes_dict[id])
        elif id in processing_parameters.forward_models.ids:
            _recommend_box(forward_model_boxes_dict[id])

    def _recommend_box(box: LabeledCheckbox):
        box.color = "green"
        box.font_weight = "bold"

    def _discourage(id: str):
        if id in processing_parameters.variables.ids:
            _discourage_box(variable_boxes_dict[id])
        elif id in processing_parameters.forward_models.ids:
            _discourage_box(forward_model_boxes_dict[id])

    def _discourage_box(box: LabeledCheckbox):
        box.color = "black"
        box.font_weight = "normal"

    def _regular(id: str):
        if id in processing_parameters.variables.ids:
            _regular_box(variable_boxes_dict[id])
        elif id in processing_parameters.forward_models.ids:
            _regular_box(forward_model_boxes_dict[id])

    def _regular_box(box: LabeledCheckbox):
        box.color = "black"
        box.font_weight = "bold"

    def _invalid(id: str):
        if id in processing_parameters.variables.ids:
            _invalid_box(variable_boxes_dict[id])
        elif id in processing_parameters.forward_models.ids:
            _invalid_box(forward_model_boxes_dict[id])

    def _invalid_box(box: LabeledCheckbox):
        box.color = "red"
        box.font_weight = "bold"

    def _request_status() -> str:
        if len(selected_variables) == 0 and len(selected_forward_models) == 0:
            return 'No variable or forward model selected'
        elif len(selected_variables) == 0:
            return 'No variable selected'
        elif len(selected_forward_models) == 0:
            return 'No forward model selected'
        else:
            for selected_variable in selected_variables:
                forward_model_available = False
                for variable_fm in forward_models_per_variable[selected_variable]:
                    if variable_fm in selected_forward_models:
                        forward_model_available = True
                        break
                if not forward_model_available:
                    return f"No forward model selected for variable '{selected_variable}'"
            for input_type in processing_parameters.input_types.ids:
                if len(selected_forward_models_per_type[input_type]) > 1:
                    fm1 = selected_forward_models_per_type[input_type][0]
                    fm2 = selected_forward_models_per_type[input_type][1]
                    return f"Invalid selection: Forward model '{fm1}' and forward model '{fm2}' " \
                           f"are both of input '{input_type}'"
            return 'Selection is valid'

    def _update_request_validation():
        color = 'red'
        request_status = _request_status()
        if request_status == 'Selection is valid':
            color = 'green'
        request_validation.value=html_element('h5', att=dict(style=f'color:{color}'), value=request_status)

    def _handle_variable_selection(change: dict):
        if change['name'] is not '_property_lock':
            return
        selected_variable_id = change['owner'].description
        _validate_variable(selected_variable_id)
        if change['new']['value']:
            selected_variables.append(selected_variable_id)
        else:
            selected_variables.remove(selected_variable_id)
        _update_request_validation()
        for fm_id in forward_models_per_variable[selected_variable_id]:
            if fm_id in selected_forward_models:
                if len(selected_forward_models_per_type[_fm_input_type(fm_id)]) > 1:
                    _invalid(fm_id)
                else:
                    _recommend(fm_id)
            else:
                if len(selected_forward_models_per_type[_fm_input_type(fm_id)]) > 0:
                    _discourage(fm_id)
                else:
                    for fm_variable in _fm_variables(fm_id):
                        if fm_variable in selected_variables:
                            _recommend(fm_id)
                            return
                    _regular(fm_id)

    def _validate_variable(variable: str):
        selected_fms = []
        selected_fm_types = []
        num_forward_models_in_conflict = 0
        for fm_id in forward_models_per_variable[variable]:
            num_allowed_selected_forward_models_per_type = 0
            fm_it = _fm_input_type(fm_id)
            if fm_id in selected_forward_models:
                selected_fms.append(fm_id)
                if fm_it not in selected_fm_types:
                    selected_fm_types.append(fm_it)
                num_allowed_selected_forward_models_per_type = 1
            if len(selected_forward_models_per_type[fm_it]) > num_allowed_selected_forward_models_per_type:
                num_forward_models_in_conflict += 1
        if num_forward_models_in_conflict == len(forward_models_per_variable[variable]):
            if variable in selected_variables:
                _invalid(variable)
            else:
                _discourage(variable)
        elif variable in selected_variables:
            _recommend(variable)
        elif len(selected_fms) == 0:
            _regular(variable)
        elif len(selected_fms) == 1:
            _recommend(variable)
        elif len(selected_fms) == len(selected_fm_types):
            _recommend(variable)
        else:
            _discourage(variable)

    @debug_view.capture(clear_output=True)
    def _handle_forward_model_selection(change: dict):
        if change['name'] is not '_property_lock':
            return
        selected_fm_id = change['owner'].description
        selected_fm_it = _fm_input_type(selected_fm_id)
        if change['new']['value']:
            selected_forward_models.append(selected_fm_id)
            selected_forward_models_per_type[selected_fm_it].append(selected_fm_id)
        else:
            selected_forward_models.remove(selected_fm_id)
            selected_forward_models_per_type[selected_fm_it].remove(selected_fm_id)
        _update_request_validation()
        for available_forward_model in available_forward_models_per_type[selected_fm_it]:
            at_least_one_variable_selected = False
            for fm_variable in _fm_variables(available_forward_model):
                _validate_variable(fm_variable)
                if fm_variable in selected_variables:
                    at_least_one_variable_selected = True
            if len(selected_forward_models_per_type[selected_fm_it]) == 0:
                if at_least_one_variable_selected:
                    _recommend(available_forward_model)
                else:
                    _regular(available_forward_model)
            elif available_forward_model not in selected_forward_models_per_type[selected_fm_it]:
                _discourage(available_forward_model)
            elif len(selected_forward_models_per_type[selected_fm_it]) == 1:
                _recommend(available_forward_model)
            else:
                _invalid(available_forward_model)

    # noinspection PyTypeChecker
    variables_box = _wrap_checkboxes_in_widget(variable_boxes_dict.values(), _handle_variable_selection)
    # noinspection PyTypeChecker
    forward_models_box = _wrap_checkboxes_in_widget(forward_model_boxes_dict.values(), _handle_forward_model_selection)

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
        request_status = _request_status()
        if request_status != 'Selection is valid':
            output.value = html_element('h5', att=dict(style='color:red'), value=request_status)
            return
        input_types = []
        for input_type in selected_forward_models_per_type:
            if len(selected_forward_models_per_type[input_type]) > 0:
                input_types.append(input_type)
        roi_data = leaflet_map.layers[1].data
        if not roi_data:
            output.value = html_element('h5', att=dict(style='color:red'),
                                        value=f'Error: No region of Interest specified')
            return
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

        if inputs_request is not None:
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

        if inputs_request is not None:
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
        widgets.Box([request_validation], layout=form_item_layout),
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


def _get_checkboxes_dict(ids: List[str]) -> dict:
    checkboxes = {}
    for var_id in ids:
        checkbox = LabeledCheckbox(value=False, description=var_id, font_weight="bold")
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
