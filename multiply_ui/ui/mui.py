from multiply_ui.ui.procparams import get_proc_params, ProcessingParameters


class MultiplyUI:
    def __init__(self):
        self._proc_params = None

    @property
    def proc_params(self) -> ProcessingParameters:
        if self._proc_params is None:
            self._proc_params = get_proc_params()
        return self._proc_params


mui = MultiplyUI()
