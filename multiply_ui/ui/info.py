import ipywidgets as widgets
from ..util.html import html_element

from typing import List


class InfoComponent:

    def __init__(self):
        self.output = widgets.HTML()
        self.info_box = widgets.Output(layout={'border': '0px solid black'})
        self.traceback = []

        def handle_more_info_button_clicked(*args, **kwargs):
            self.info_box.clear_output()
            if self.more_info_button.icon == "chevron-circle-down":
                with self.info_box:
                    for line in self.traceback:
                        print(line)
                self.more_info_button.icon = "chevron-circle-up"
            else:
                self.more_info_button.icon = "chevron-circle-down"

        self.more_info_button = widgets.Button(icon="chevron-circle-down",
                                               tooltip="Show more information about an error",
                                               layout=widgets.Layout(width='5%'))
        self.more_info_button.on_click(handle_more_info_button_clicked)
        self.more_info_button.disabled = True

    def as_widget(self):
        form_item_layout = widgets.Layout(
            display='flex',
            flex_flow='row',
            justify_content='space-between',
        )
        info_items = [
            widgets.Box([self.output, self.more_info_button], layout=form_item_layout),
            widgets.Box([self.info_box], layout=form_item_layout)
        ]
        form = widgets.Box(info_items, layout=widgets.Layout(
            display='flex',
            flex_flow='column',
            align_items='stretch',
            width='100%'
        ))
        return form

    def message_func(self, message: str, stack_trace=None):
        if stack_trace is None:
            stack_trace = []
        self.output.value = html_element('h5', value=message)
        self.traceback.clear()
        for line in stack_trace:
            self.traceback.append(line)
        self.more_info_button.disabled = len(self.traceback) == 0

    def output_html(self, html: html_element):
        self.output.value = html
        self._collapse_info_box()

    def output_message(self, message: str):
        self.output.value = html_element('h5', value=message)
        self._collapse_info_box()

    def output_error(self, error_message: str):
        self.output.value = html_element('h5', att=dict(style='color:red'), value=error_message)
        self._collapse_info_box()

    def _collapse_info_box(self):
        self.info_box.clear_output()
        self.more_info_button.icon = "chevron-circle-down"
        self.more_info_button.disabled = True
