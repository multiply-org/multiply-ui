from typing import Optional, List

from .model import Job

import multiply_data_access.data_access_component

class ServiceContext:
    def __init__(self):
        self._jobs = {}
        self.data_access_component = multiply_data_access.data_access_component.DataAccessComponent()
        self._get_mundi_datastore()

    def _get_mundi_datastore(self):
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
