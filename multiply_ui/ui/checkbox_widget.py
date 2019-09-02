import ipywidgets as widgets
# import ipywidgets as widgets
from traitlets import Bool, CInt, CUnicode, Integer, Unicode


@widgets.register
class LabeledCheckbox(widgets.DOMWidget):
    """Displays a boolean `value` in the form of a checkbox.
    Parameters
    ----------
    color : str
        Color in which the label is printed.
    enabled : {True,False}
        Whether the checkbox is enabled to be checked.
    font-weight : str
        The font weight in which the label is printed.
    indent : {True,False}
        indent the control to align with other controls with a description. The style.description_width attribute
        controls this width for consistence with other controls.
    label_text : str
        Text of the checkbox label.
    selected : {True,False}
        value of the checkbox: True-checked, False-unchecked
    tooltip : str
        The tooltip for the checkbox and the label.
    """
    _view_name = Unicode('LabeledCheckboxView').tag(sync=True)
    _view_module = Unicode('multiply-widgets').tag(sync=True)
    _view_module_version = Unicode('0.1.0').tag(sync=True)
    color = Unicode("black", help="Color in which the label is printed.").tag(sync=True)
    enabled = Bool(True, help="Whether the checkbox is enabled to be checked.").tag(sync=True)
    font_weight = Unicode("normal", help="The font weight in which the label is printed.").tag(sync=True)
    indent = Bool(False, help="Indent the control to align with other controls with a description.").tag(sync=True)
    label_text = Unicode('', help="Text of the checkbox label.").tag(sync=True)
    selected = Bool(False, help="Whether the checkbox is selected.").tag(sync=True)
    tooltip = Unicode(None, allow_none=True, help="The tooltip for the checkbox and the label.").tag(sync=True)

    def __init__(self, value=None, **kwargs):
        if value is not None:
            kwargs['value'] = value
        super().__init__(**kwargs)

    def _repr_keys(self):
        for key in super(LabeledCheckbox, self)._repr_keys():
            yield key
