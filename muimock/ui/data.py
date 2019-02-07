import datetime

from ipywidgets import Layout, Button, Box, Label, DatePicker, SelectionRangeSlider, Text


def data_ui():
    form_item_layout = Layout(
        display='flex',
        flex_flow='row',
        justify_content='space-between',
    )

    start_date = DatePicker(value=datetime.datetime(year=2010, month=1, day=1))
    end_date = DatePicker(value=datetime.datetime(year=2019, month=1, day=1))

    def format_angle(a):
        if a < 0:
            return f" {a} "
        if a > 0:
            return f" +{a} "
        return " 0 "

    lon_range = SelectionRangeSlider(
        options=[(format_angle(i - 180), i) for i in range(0, 361)],
        index=(0, 360)
    )

    lat_range = SelectionRangeSlider(
        options=[(format_angle(i - 90), i) for i in range(0, 181)],
        index=(0, 180)
    )

    form_items = [
        Box([Label(value='Dataset name'), Text()], layout=form_item_layout),
        Box([Label(value='Start date'), start_date], layout=form_item_layout),
        Box([Label(value='End date'), end_date], layout=form_item_layout),
        Box([Label(value='Longitude'), lon_range], layout=form_item_layout),
        Box([Label(value='Latitude'), lat_range], layout=form_item_layout),
        Box([Label(value=''), Button(description="Search", icon="search")], layout=form_item_layout),
    ]

    form = Box(form_items, layout=Layout(
        display='flex',
        flex_flow='column',
        border='solid 1px lightgray',
        align_items='stretch',
        width='50%'
    ))

    return form
