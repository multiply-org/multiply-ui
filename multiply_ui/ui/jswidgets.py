import ipywidgets as widgets
from traitlets import Integer, Unicode

@widgets.register
class Spinner(widgets.DOMWidget):
    _view_name = Unicode('SpinnerView').tag(sync=True)
    _view_module = Unicode('multiply-widgets').tag(sync=True)
    _view_module_version = Unicode('0.1.0').tag(sync=True)
    value = Integer(10).tag(sync=True)
