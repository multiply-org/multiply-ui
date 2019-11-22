from typing import Optional, List

import multiply_data_access.data_access_component
from multiply_core.models import get_forward_models
from multiply_core.observations import INPUT_TYPES
from multiply_core.variables import get_registered_variables
from vm_support import set_earth_data_authentication, set_mundi_authentication

from .model import Job


class ServiceContext:

    def __init__(self):
        self._jobs = {}
        self.data_access_component = multiply_data_access.data_access_component.DataAccessComponent()
        self._restrict_to_mundi_datastore()

    # TODO: require an interface of data access to select data stores to be used
    def _restrict_to_mundi_datastore(self):
        for data_store in self.data_access_component._data_stores:
            if data_store._id == "Mundi":
                self.data_access_component._data_stores = [data_store]
                return
        raise ValueError('data store Mundi not found in configuration')

    def new_job(self, duration: int) -> Job:
        job = Job(duration)
        self._jobs[job.id] = job
        return job

    def get_job(self, job_id: int) -> Optional[Job]:
        return self._jobs.get(job_id)

    def get_jobs(self) -> List[Job]:
        return [job.to_dict() for job in self._jobs.values()]

    @staticmethod
    def get_available_forward_models() -> List[dict]:
        dict_list = []
        forward_models = get_forward_models()
        for model in forward_models:
            dict_list.append({
                "id": model.id,
                "name": model.name,
                "description": model.description,
                "modelAuthors": model.authors,
                "modelUrl": model.url,
                "inputType": model.model_data_type,
                "variables": model.variables
            })
        return dict_list

    @staticmethod
    def get_available_input_types() -> List[dict]:
        input_types = []
        for input_type in INPUT_TYPES:
            input_types.append({"id": input_type, "name": INPUT_TYPES[input_type]["input_data_type_name"],
                                "timeRange": INPUT_TYPES[input_type]["timeRange"]})
        return input_types

    @staticmethod
    def get_available_variables() -> List[dict]:
        dict_list = []
        variables = get_registered_variables()
        for variable in variables:
            dict_list.append({
                "id": variable.short_name,
                "name": variable.display_name,
                "unit": variable.unit,
                "description": variable.description,
                "valueRange": variable.range,
                "applications": variable.applications
            })
        return dict_list

    @staticmethod
    def set_earth_data_authentication(username: str, password: str):
        set_earth_data_authentication(username, password)

    @staticmethod
    def set_mundi_authentication(access_key_id: str, secret_access_key: str):
        set_mundi_authentication(access_key_id, secret_access_key)
