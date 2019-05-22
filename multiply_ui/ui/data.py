import datetime
from typing import Any, Dict, List

import ipywidgets as widgets
from ..server.config import SUPPORTED_VARIABLES
_PROC_REQUESTS = list()


def get_proc_requests() -> List[Dict[str, Any]]:
    return _PROC_REQUESTS


def get_proc_request(pr_id: str) -> Dict[str, Any]:
    return next(filter(lambda pr: pr['id'] == pr_id, _PROC_REQUESTS), None)


def data_ui():
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

    num_cols = 4
    v_box_item_lists = [[] for i in range(num_cols)]
    index = 0
    for var_name in SUPPORTED_VARIABLES:
        col = index % num_cols
        v_box_item_lists[col].append(widgets.Checkbox(
            value=False,
            description=var_name,
            disabled=False
        ))
        # left_box = widgets.VBox([items[0], items[1]])
        index += 1

    v_boxes = []
    for v_box_item_list in v_box_item_lists:
        v_boxes.append(widgets.VBox(v_box_item_list))
    h_box = widgets.HBox(v_boxes)


    #output_variables =

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
        try:
            _PROC_REQUESTS.append(dict(
                requestName=request_name.value or f"Request #{1 + len(_PROC_REQUESTS)}",
                startDate=str(start_date.value),
                endDate=str(end_date.value),
                lonRange=lon_range.value,
                latRange=lat_range.value,
            ))
        except Exception:
            import traceback
            traceback.print_exc()

    new_button = widgets.Button(description="New", icon="search")
    new_button.on_click(handle_new_button_clicked)
    form_items = [
        widgets.Box([widgets.Label(value='Output variables')], layout=form_item_layout),
        widgets.Box([h_box], layout=var_checks_layout),
        widgets.Box([widgets.Label(value='Forward models')], layout=form_item_layout),
        widgets.Box([h_box], layout=var_checks_layout),
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
