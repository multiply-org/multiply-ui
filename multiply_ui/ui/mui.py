from .procparams import get_processing_parameters, ProcessingParameters, Variables, ForwardModels, InputTypes
from .inputs import inputs_ui


class MultiplyUI:
    def __init__(self):
        self._processing_parameters = None

    @property
    def processing_parameters(self) -> ProcessingParameters:
        if self._processing_parameters is None:
            self._processing_parameters = get_processing_parameters()
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

    def inputs(self):
        return inputs_ui(self.processing_parameters)


mui = MultiplyUI()
