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
from ..jswidgets import LabeledCheckbox, Spinner
from ..params.model import ProcessingParameters
from ...util.html import html_element, html_table
from ..info import InfoComponent

_NUM_REQUESTS = 0


def sel_params_form(processing_parameters: ProcessingParameters, identifier='identifier', name='name', mock=False):
    debug_view = get_debug_view()

    fetch_inputs_func = fetch_inputs
    if mock:
        @debug_view.capture(clear_output=True)
        def fetch_inputs_mock(input_request: InputRequest, message_func) -> ProcessingRequest:
            debug_view.value = ''
            time.sleep(2)
            input_identifiers = {input_type: [f'iid-{i}' for i in range(10)] for input_type in
                                 input_request.input_types}
            processing_request_data = input_request.as_dict()
            processing_request_data.update(dict(inputIdentifiers=input_identifiers))
            return ProcessingRequest(processing_request_data)

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

    variable_names = []
    for variable_id in processing_parameters.variables.ids:
        variable_names.append(processing_parameters.variables.get(variable_id).name)
    forward_model_names = []
    for model_id in processing_parameters.forward_models.ids:
        forward_model_names.append(processing_parameters.forward_models.get(model_id).name)
    variable_boxes_dict = _get_checkboxes_dict(processing_parameters.variables.ids, variable_names)
    forward_model_boxes_dict = _get_checkboxes_dict(processing_parameters.forward_models.ids, forward_model_names)
    request_validation = widgets.HTML(value=html_element('h3',
                                                         att=dict(style='color:red'),
                                                         value='No variable or forward model selected'))
    non_disabled_forward_models = []
    available_forward_models_per_type = {}
    forward_models_per_variable = {}
    forward_model_select_buttons = {}
    for fm_id in processing_parameters.forward_models.ids:
        non_disabled_forward_models.append(fm_id)
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
    selected_forward_model_per_type = {}
    for it in processing_parameters.input_types.ids:
        selected_forward_model_per_type[it] = None

    def _fm_variables(fm_id: str):
        return processing_parameters.forward_models.get(fm_id).variables

    def _fm_input_type(fm_id: str):
        return processing_parameters.forward_models.get(fm_id).input_type

    def _recommend(id: str):
        if id in processing_parameters.variables.ids:
            _recommend_box(variable_boxes_dict[id])
        elif id in processing_parameters.forward_models.ids:
            if id not in non_disabled_forward_models:
                non_disabled_forward_models.append(id)
            _recommend_box(forward_model_boxes_dict[id])

    def _recommend_box(box: LabeledCheckbox):
        box.enabled = True
        box.color = "green"
        box.font_weight = "bold"

    def _disable(id: str):
        if id in processing_parameters.variables.ids:
            _disable_box(variable_boxes_dict[id])
        elif id in processing_parameters.forward_models.ids:
            if id in non_disabled_forward_models:
                non_disabled_forward_models.remove(id)
            _disable_box(forward_model_boxes_dict[id])

    def _disable_box(box: LabeledCheckbox):
        box.enabled = False
        box.font_weight = "normal"

    def _display_normally(id: str):
        if id in processing_parameters.variables.ids:
            _display_normally_box(variable_boxes_dict[id])
        elif id in processing_parameters.forward_models.ids:
            if id not in non_disabled_forward_models:
                non_disabled_forward_models.append(id)
            _display_normally_box(forward_model_boxes_dict[id])

    def _display_normally_box(box: LabeledCheckbox):
        box.enabled = True
        box.color = "black"
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
                    return f"Variable '{selected_variable}' cannot be derived with any of the selected forward models."
            for selected_forward_model in selected_forward_models:
                at_least_one_variable_selected = False
                for variable in processing_parameters.forward_models.get(selected_forward_model).variables:
                    if variable in selected_variables:
                        at_least_one_variable_selected = True
                        break
                if not at_least_one_variable_selected:
                    return f"Selection is valid, " \
                           f"but no variable is selected for forward model '{selected_forward_model}'."
            return 'Selection is valid'

    def _validate_selection():
        color = 'red'
        request_status = _request_status()
        if request_status.startswith('Selection is valid'):
            if request_status == 'Selection is valid':
                color = 'green'
            else:
                color = 'orange'
            request_status = _format_request_status(request_status)
        request_validation.value=html_element('h3', att=dict(style=f'color:{color}'), value=request_status)

    def _format_request_status(request_status: str) -> str:
        if not request_status.startswith('Selection is valid'):
            return request_status
        forward_model_lines = []
        for forward_model_id in selected_forward_models:
            fm_selected_variables = []
            fm_variables = processing_parameters.forward_models.get(forward_model_id).variables
            for fm_variable in fm_variables:
                if fm_variable in selected_variables:
                    fm_selected_variables.append(f"'{fm_variable}'")
            if len(fm_selected_variables) > 0:
                fm_selected_variables = ', '.join(fm_selected_variables)
                forward_model_lines.append(f"With model '{forward_model_id}': Compute {fm_selected_variables}")
            else:
                forward_model_lines.append(f"Model '{forward_model_id}' "
                                           f"is selected, but does not compute any variables")
        forward_model_lines = '<br>'.join(forward_model_lines)
        message = f"{request_status}:<br>{forward_model_lines}"
        return message

    def _handle_variable_selection(change: dict):
        if change['name'] is not '_property_lock':
            return
        variable_id = change['owner'].label_text
        if change['new']['selected']:
            selected_variables.append(variable_id)
        else:
            selected_variables.remove(variable_id)
        _update_forward_models_after_variable_change(variable_id, True)
        _validate_selection()

    def _update_forward_models_after_variable_change(variable_id: str, examine_secondary_models: bool=False):
        already_examined_types = []
        for potential_forward_model in forward_models_per_variable[variable_id]:
            fm_type = _fm_input_type(potential_forward_model)
            if (selected_forward_model_per_type[fm_type]) is not None or fm_type in already_examined_types:
                continue
            _validate_forward_models_of_type(fm_type)
            _validate_variables_of_forward_models_of_type(fm_type)
            if examine_secondary_models:
                _validate_forward_models_of_variables_of_forward_models_of_type(fm_type)
            already_examined_types.append(fm_type)

    def _validate_forward_models_of_type(fm_type: str):
        for fm_of_same_type in available_forward_models_per_type[fm_type]:
            if selected_forward_model_per_type[fm_type] == fm_of_same_type:
                _recommend(fm_of_same_type)
                continue
            if selected_forward_model_per_type[fm_type] is not None:
                _disable(fm_of_same_type)
                continue
            fm_of_same_type_variables = _fm_variables(fm_of_same_type)
            at_least_one_variable_selected = False
            for fm_of_same_type_variable in fm_of_same_type_variables:
                if fm_of_same_type_variable in selected_variables:
                    afms_for_st_variable = _available_forward_models_for_variable(fm_of_same_type_variable)
                    if len(afms_for_st_variable) == 1 and _fm_input_type(afms_for_st_variable[0]) == fm_type:
                        _recommend(fm_of_same_type)
                        for other_fm_of_same_type in available_forward_models_per_type[fm_type]:
                            if other_fm_of_same_type != fm_of_same_type:
                                _disable(other_fm_of_same_type)
                        return
                    at_least_one_variable_selected = True
            if at_least_one_variable_selected:
                _recommend(fm_of_same_type)
            else:
                _display_normally(fm_of_same_type)

    def _validate_variables_of_forward_models_of_type(fm_type: str):
        for fm_of_same_type in available_forward_models_per_type[fm_type]:
            fm_of_same_type_variables = _fm_variables(fm_of_same_type)
            for fm_of_same_type_variable in fm_of_same_type_variables:
                _validate_variable(fm_of_same_type_variable)

    def _validate_forward_models_of_variables_of_forward_models_of_type(fm_type: str):
        for fm_of_same_type in available_forward_models_per_type[fm_type]:
            fm_of_same_type_variables = _fm_variables(fm_of_same_type)
            for fm_of_same_type_variable in fm_of_same_type_variables:
                afms_for_same_type_variable = _available_forward_models_for_variable(fm_of_same_type_variable)
                if _fm_input_type(afms_for_same_type_variable[0]) != fm_type:
                    _validate_forward_models_of_type(_fm_input_type(afms_for_same_type_variable[0]))
                    _validate_variables_of_forward_models_of_type(_fm_input_type(afms_for_same_type_variable[0]))

    def _available_forward_models_for_variable(variable_id: str) -> List[str]:
        available_forward_models_for_variable = []
        for model_id in forward_models_per_variable[variable_id]:
            if model_id in non_disabled_forward_models:
                available_forward_models_for_variable.append(model_id)
        return available_forward_models_for_variable

    def _validate_variable(variable: str):
        if variable in selected_variables:
            _recommend(variable)
            return
        available_forward_models_for_variable = _available_forward_models_for_variable(variable)
        if len(available_forward_models_for_variable) == 0:
            _disable(variable)
            return
        for available_forward_model_for_variable in available_forward_models_for_variable:
            if available_forward_model_for_variable in selected_forward_models:
                _recommend(variable)
                return
        _display_normally(variable)

    @debug_view.capture(clear_output=True)
    def _handle_forward_model_selection(change: dict):
        if change['name'] is not '_property_lock':
            return
        selected_fm_id = change['owner'].label_text
        selected_fm_it = _fm_input_type(selected_fm_id)
        if change['new']['selected']:
            selected_forward_models.append(selected_fm_id)
            selected_forward_model_per_type[selected_fm_it] = selected_fm_id
            forward_model_select_buttons[selected_fm_id].disabled = False
        else:
            selected_forward_models.remove(selected_fm_id)
            selected_forward_model_per_type[selected_fm_it] = None
            forward_model_select_buttons[selected_fm_id].disabled = True
        _validate_forward_models_of_type(selected_fm_it)
        _validate_variables_of_forward_models_of_type(selected_fm_it)
        _validate_selection()

    def _clear_variable_selection(b):
        for variable_id in variable_boxes_dict:
            if variable_id in selected_variables:
                selected_variables.remove(variable_id)
                variable_boxes_dict[variable_id].selected = False
                _validate_variable(variable_id)
                _update_forward_models_after_variable_change(variable_id)
        _validate_selection()

    output = widgets.HTML()

    def _clear_forward_model_selection(b):
        affected_input_types = []
        for forward_model_id in forward_model_boxes_dict:
            if forward_model_id in selected_forward_models:
                selected_forward_models.remove(forward_model_id)
                forward_model_type = _fm_input_type(forward_model_id)
                selected_forward_model_per_type[forward_model_type] = None
                if forward_model_type not in affected_input_types:
                    affected_input_types.append(forward_model_type)
                forward_model_boxes_dict[forward_model_id].selected = False
        for input_type in affected_input_types:
            _validate_forward_models_of_type(input_type)
            _validate_variables_of_forward_models_of_type(input_type)
        _validate_selection()

    def _select_all_variables_for_forward_model(forward_model_id: str):
        fm_variables = _fm_variables(forward_model_id)
        for variable_id in fm_variables:
            if variable_id not in selected_variables:
                selected_variables.append(variable_id)
                variable_boxes_dict[variable_id].selected = True
                _update_forward_models_after_variable_change(variable_id)
        _validate_selection()

    # noinspection PyTypeChecker
    variables_box = _wrap_variable_checkboxes_in_widget(variable_boxes_dict.values(), _handle_variable_selection)
    clear_variable_selection_button = widgets.Button(description="Clear Variable Selection",
                                                     layout=widgets.Layout(left='60%', width='35%'))
    clear_variable_selection_button.on_click(_clear_variable_selection)
    forward_model_variables = {}
    for fm_id in processing_parameters.forward_models.ids:
        forward_model_variables[fm_id] = processing_parameters.forward_models.get(fm_id).variables
        forward_model_select_buttons[fm_id] = _get_select_button(_select_all_variables_for_forward_model, fm_id)

    # noinspection PyTypeChecker
    forward_models_box = _wrap_forward_model_checkboxes_in_widget(forward_model_boxes_dict.values(),
                                                                  forward_model_select_buttons,
                                                                  _handle_forward_model_selection,
                                                                  forward_model_variables)
    clear_model_selection_button = widgets.Button(description="Clear Forward Model Selection",
                                                  layout=widgets.Layout(left='60%', width='35%'))
    clear_model_selection_button.on_click(_clear_forward_model_selection)

    global _NUM_REQUESTS
    _NUM_REQUESTS += 1
    request_name = widgets.Text(name)
    python_var_name = widgets.Text(identifier)

    start_date = widgets.DatePicker(value=datetime.datetime(year=2018, month=6, day=1))
    end_date = widgets.DatePicker(value=datetime.datetime(year=2018, month=6, day=10))

    time_steps = Spinner(
        value=10,
        min = 1
    )

    time_steps_unit = widgets.Dropdown(
        options=['days', 'weeks'],
        value='days',
        disabled=False
    )

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

    spatial_resolution = Spinner(
        value=100,
        min = 1,
        step = 1
    )

    info = InfoComponent()

    def new_input_request():
        request_status = _request_status()
        if request_status != 'Selection is valid':
            info.output_error(request_status)
            return
        input_types = []
        for input_type in selected_forward_model_per_type:
            if selected_forward_model_per_type[input_type] is not None:
                input_types.append(input_type)
        roi_data = leaflet_map.layers[1].data
        if not roi_data:
            info.output_error('Error: No region of Interest specified')
            return
        roi = shape(roi_data)
        x1, y1, x2, y2 = roi.bounds

        return InputRequest(dict(
            name=request_name.value,
            timeRange=[datetime.datetime.strftime(start_date.value, "%Y-%m-%d"),
                       datetime.datetime.strftime(end_date.value, "%Y-%m-%d")],
            timeStep=time_steps.value,
            timeStepUnit=time_steps_unit.value,
            bbox=f"{x1},{y1},{x2},{y2}",
            spatialResolution=spatial_resolution.value,
            inputTypes=input_types,
            parameters=selected_variables
        ))

    # noinspection PyUnusedLocal
    @debug_view.capture(clear_output=True)
    def handle_new_button_clicked(*args, **kwargs):
        req_var_name = python_var_name.value or 'req'
        if req_var_name and not req_var_name.isidentifier():
            info.output_error(f'Error: invalid Python identifier: {req_var_name}')
            return

        inputs_request = new_input_request()
        if inputs_request is None:
            return
        info.output_message('Fetching results...')

        processing_request = fetch_inputs_func(inputs_request, info.message_func)

        if processing_request is None:
            return
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
        info.output_html(result_html)

    # noinspection PyUnusedLocal
    @debug_view.capture(clear_output=True)
    def handle_submit_button_clicked(*args, **kwargs):
        req_var_name = python_var_name.value or 'job'
        if req_var_name and not req_var_name.isidentifier():
            info.output_error(f'Error: invalid Python identifier: {req_var_name}')
            return

        inputs_request = new_input_request()

        info.output_message('Submitting processing request...')

        job = submit_processing_request(inputs_request, message_func=info.message_func, mock=mock)
        if job is not None:
            shell = IPython.get_ipython()
            shell.push({req_var_name: job}, interactive=True)
            result_html = html_element('p',
                                       value=f'Note: a new job is currently being executed and is '
                                       f'stored in variable <code>{req_var_name}</code>.')
            info.output_html(result_html)

    # TODO: make GUI form look nice
    new_button = widgets.Button(description="New Request", icon="search")
    new_button.on_click(handle_new_button_clicked)
    submit_button = widgets.Button(description="Submit Request", icon="upload")
    submit_button.on_click(handle_submit_button_clicked)
    form_items = [
        widgets.Box([widgets.HTML(value=html_element('h2', value='Output Variables'))], layout=form_item_layout),
        widgets.Box([variables_box], layout=var_checks_layout),
        widgets.Box([clear_variable_selection_button], layout=form_item_layout),
        widgets.Box([widgets.HTML(value=html_element('h2', value='Forward Models'))], layout=form_item_layout),
        widgets.Box([forward_models_box], layout=var_checks_layout),
        widgets.Box([clear_model_selection_button], layout=form_item_layout),
        widgets.Box([request_validation], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Start date'), start_date], layout=form_item_layout),
        widgets.Box([widgets.Label(value='End date'), end_date], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Time steps'), widgets.Box([time_steps, time_steps_unit])],
                    layout=form_item_layout),
        widgets.Box([widgets.Label(value="Region of Interest"), leaflet_map], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Resolution (m)'), spatial_resolution], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Request/job name'), request_name], layout=form_item_layout),
        widgets.Box([widgets.Label(value='Python identifier'), python_var_name], layout=form_item_layout),
        widgets.Box([widgets.Label(value=''), widgets.Box([new_button, submit_button])], layout=form_item_layout),
        widgets.Box([info.as_widget()], layout=form_item_layout)
    ]

    form = widgets.Box(form_items, layout=widgets.Layout(
        display='flex',
        flex_flow='column',
        border='solid 1px lightgray',
        align_items='stretch',
        width='50%'
    ))

    return form


def _get_select_button(_select, f_model_id):
    select_button = widgets.Button(description=f"Select all variables", height=10, disabled=True,
                                   layout=widgets.Layout(flex='0 1 50%', align_self='flex-end'))

    def _apply_func(b):
        _select(f_model_id)

    select_button.on_click(_apply_func)
    return select_button


def _get_checkboxes_dict(ids: List[str], names: List[str]) -> dict:
    checkboxes = {}
    for i, var_id in enumerate(ids):
        checkbox = LabeledCheckbox(selected=False, label_text=var_id, tooltip=names[i], font_weight="bold",
                                   layout=widgets.Layout(flex='0 1 78%'))
        checkboxes[var_id] = checkbox
    return checkboxes


def _wrap_variable_checkboxes_in_widget(checkboxes: List[widgets.Checkbox], handle_selection) -> widgets.Widget:
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
        v_box_layout = widgets.Layout(
            overflow='hidden',
            width='25%',
            display='flex'
        )
        v_box = widgets.VBox(v_box_item_list, layout=v_box_layout)
        v_boxes.append(v_box)
    h_box_layout = widgets.Layout(
        overflow='hidden',
        display='flex'
    )
    h_box = widgets.HBox(v_boxes, layout=h_box_layout)
    return h_box


def _wrap_forward_model_checkboxes_in_widget(checkboxes: List[widgets.Checkbox], select_all_buttons: dict,
                                             handle_selection, forward_model_variables: dict) -> widgets.Widget:
    num_cols = 4
    # noinspection PyUnusedLocal
    v_box_item_lists = [[] for i in range(num_cols)]
    index = 0
    for checkbox in checkboxes:
        col = index % num_cols
        checkbox.observe(handle_selection)
        fm_variables = forward_model_variables[checkbox.label_text]
        fm_variables = ', '.join(fm_variables)
        tooltip_message = f'Variables that can be computed with this forward model: {fm_variables}'
        icon_button = widgets.Button(description='', tooltip=tooltip_message, width=5, icon='question-circle',
                                     disabled=True, layout=widgets.Layout(flex='0 1 22%'))
        icon_button.style.button_color = 'white'
        h_box = widgets.HBox([checkbox, icon_button], layout=widgets.Layout(flex='0 1 50%'))
        # noinspection PyTypeChecker
        v_box = widgets.Box([h_box, select_all_buttons[checkbox.label_text]],
                            layout=widgets.Layout(display='flex', flex_flow='column'))
        v_box_item_lists[col].append(v_box)
        index += 1
    v_boxes = []
    for v_box_item_list in v_box_item_lists:
        v_box_layout = widgets.Layout(
            overflow='hidden',
            width='25%',
            display='flex'
        )
        v_box = widgets.VBox(v_box_item_list, layout=v_box_layout)
        v_boxes.append(v_box)
    h_box_layout = widgets.Layout(
        overflow='hidden',
        display='flex'
    )
    h_box = widgets.HBox(v_boxes, layout=h_box_layout)
    return h_box
