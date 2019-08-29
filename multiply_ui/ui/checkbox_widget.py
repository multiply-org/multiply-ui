import ipywidgets as widgets
# import ipywidgets as widgets
from traitlets import Bool, CInt, CUnicode, Integer, Unicode


@widgets.register
class LabeledCheckbox(widgets.DOMWidget):
    """Displays a boolean `value` in the form of a checkbox.
    Parameters
    ----------
    value : {True,False}
        value of the checkbox: True-checked, False-unchecked
    description : str
        description displayed next to the checkbox
    indent : {True,False}
        indent the control to align with other controls with a description. The style.description_width attribute controls this width for consistence with other controls.
    """
    value = Bool(True, help="Bool value").tag(sync=True)
    _view_name = Unicode('LabeledCheckboxView').tag(sync=True)
    _view_module = Unicode('multiply-widgets').tag(sync=True)
    _view_module_version = Unicode('0.1.0').tag(sync=True)
    indent = Bool(False, help="Indent the control to align with other controls with a description.").tag(sync=True)
    description = Unicode('', help="Description of the control.").tag(sync=True)
    description_tooltip = Unicode(None, allow_none=True, help="Tooltip for the description (defaults to description).").tag(sync=True)
    disabled = Bool(False, help="Bool value").tag(sync=True)
    color = Unicode("black", help="Color in which the label is printed.").tag(sync=True)
    font_weight = Unicode("normal", help="The font weight in which the label is printed.").tag(sync=True)

    def __init__(self, value=None, **kwargs):
        if value is not None:
            kwargs['value'] = value
        super().__init__(**kwargs)

    def _repr_keys(self):
        for key in super(LabeledCheckbox, self)._repr_keys():
            yield key
