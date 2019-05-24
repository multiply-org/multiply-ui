import ipywidgets as widgets
import IPython

_DEBUG_VIEW = None


def get_debug_view():
    global _DEBUG_VIEW
    if _DEBUG_VIEW is None:
        _DEBUG_VIEW = widgets.Output(layout={'border': '2px solid red'})
        shell = IPython.get_ipython()
        shell.push({'debug_view': _DEBUG_VIEW}, interactive=True)
    return _DEBUG_VIEW
