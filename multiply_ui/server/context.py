from typing import Optional, List

from .model import Job

class ServiceContext:
    def __init__(self):
        self._jobs = {}

    def new_job(self, duration: int) -> Job:
        job = Job(duration)
        self._jobs[job.id] = job
        return job

    def get_job(self, job_id: int) -> Optional[Job]:
        return self._jobs.get(job_id)

    def get_jobs(self) -> List[Job]:
        return [job.to_dict() for job in self._jobs.values()]
