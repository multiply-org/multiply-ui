from .auth.form import auth_form
from .clear.api import ClearanceType, clear
from .job.api import visualize_output
from .job.model import Job
from .job.form import obs_job_form, obs_jobs_form
from .params.api import fetch_processing_parameters
from .params.model import ProcessingParameters, Variables, ForwardModels, InputTypes, PostProcessors
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

    @property
    def post_processors(self) -> PostProcessors:
        return self.processing_parameters.post_processors
    
    @property
    def indicators(self) -> Variables:
        return self.processing_parameters.indicators

    def sel_params(self, identifier='request', name='name', mock=False):
        return sel_params_form(self.processing_parameters, identifier, name, mock=mock)

    def obs_job(self, job: Job, mock=False):
        return obs_job_form(job, mock)

    def obs_jobs(self, mock=False):
        return obs_jobs_form(mock)

    def set_auth(self):
        return auth_form()

    def clear_caches(self):
        clear(ClearanceType.CACHE)

    def clear_working_dirs(self):
        clear(ClearanceType.WORKING_DIRS)

    def clear_auxiliary(self):
        clear(ClearanceType.AUXILIARY_DATA)

    def clear_archive(self):
        clear(ClearanceType.ARCHIVED_DATA)

    def visualize(self, job: Job):
        visualize_output(job.id)


mui = MultiplyUI()
