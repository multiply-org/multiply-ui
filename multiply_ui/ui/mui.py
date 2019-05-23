from .params.api import fetch_processing_parameters
from .params.model import ProcessingParameters, Variables, ForwardModels, InputTypes
from .req.form import sel_params_form


class MultiplyUI:
    """
    Main interface users will interact within in a Jupyter Notebook.

    Property and method names are intentionally short
    so they can be remembered and quickly typed into a notebook.
    """

    def __init__(self):
        self._processing_parameters = None

    @property
    def processing_parameters(self) -> ProcessingParameters:
        if self._processing_parameters is None:
            self._processing_parameters = fetch_processing_parameters()
        return self._processing_parameters

    @property
    def vars(self) -> Variables:
        return self.processing_parameters.variables

    @property
    def models(self) -> ForwardModels:
        return self.processing_parameters.forward_models

    @property
    def itypes(self) -> InputTypes:
        return self.processing_parameters.input_types

    def sel_params(self):
        return sel_params_form(self.processing_parameters)


mui = MultiplyUI()
