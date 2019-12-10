from typing import Optional
import ipywidgets as widgets

from ..util.html import html_element


def user_prior_component(prior_name: str, unit_name: Optional[str]=None, _handle_change=None, mu=None, unc=None):
    _mu_checkbox = widgets.Checkbox(value=mu is not None, description='Value')
    _unc_checkbox = widgets.Checkbox(value=unc is not None, description='Uncertainty')
    if mu is None:
        mu = 0.5
    _mu_field = widgets.BoundedFloatText(value=mu, min=0.01, step=0.1)
    if unc is None:
        unc = 0.1
    _unc_field = widgets.BoundedFloatText(value=unc, min=0.0, step=0.05)

    def _update_state(b):
        state_dict = {prior_name: {}}
        if _mu_checkbox.value:
            state_dict[prior_name]['mu'] = _mu_field.value
        if _unc_checkbox.value:
            state_dict[prior_name]['unc'] = _unc_field.value
        _handle_change(state_dict)

    _mu_checkbox.observe(_update_state)
    _mu_field.observe(_update_state)
    _unc_checkbox.observe(_update_state)
    _unc_field.observe(_update_state)
    html_layout = widgets.Layout(
        display='flex',
        flex_flow='row',
        justify_content='center'
    )
    box_layout = widgets.Layout(
        display='flex',
        flex_flow='row'
    )
    label_text = prior_name
    if unit_name is not None and unit_name != '':
        label_text = f'{prior_name} ({unit_name})'
    items = [
        widgets.Box([widgets.HTML(value=html_element('h3', value=label_text))], layout=html_layout),
        widgets.Box([_mu_checkbox, _mu_field], layout=box_layout),
        widgets.Box([_unc_checkbox, _unc_field], layout=box_layout)
    ]
    form = widgets.Box(items, layout=widgets.Layout(
        display='flex',
        flex_flow='column',
        align_items='stretch',
        width='100%',
    ))
    return form
