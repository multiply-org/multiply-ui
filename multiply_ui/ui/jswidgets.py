import ipywidgets as widgets
from traitlets import CInt, Integer, Unicode

@widgets.register
class Spinner(widgets.DOMWidget):
    _view_name = Unicode('SpinnerView').tag(sync=True)
    _view_module = Unicode('multiply-widgets').tag(sync=True)
    _view_module_version = Unicode('0.1.0').tag(sync=True)
    value = Integer().tag(sync=True)
    min = CInt(0, help="Min value").tag(sync=True)
    step = Integer(1).tag(sync=True)
    max = CInt(1000, help="Max value").tag(sync=True)