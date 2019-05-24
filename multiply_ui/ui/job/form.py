import ipywidgets as widgets
from IPython.display import display
import threading

from .api import get_job
from .model import Job
from ..debug import get_debug_view


def obs_job(job: Job, mock=False):
    debug_view = get_debug_view()

    @debug_view.capture(clear_output=True)
    def get_job_mock(job_state: Job, apply_func):
        debug_view.value = ''
        import time
        time.sleep(1)
        job_data_dict = {
            "id": job_state.id,
            "name": job_state.name,
            "progress": 15,
            "status": "mocking",
            "tasks": [
                {
                    "name": "Fetching static Data",
                    "progress": 100,
                    "status": "mocking"
                },
                {
                    "name": "Collecting Data from 2017-06-01 to 2017-06-10",
                    "progress": 100,
                    "status": "mocking"
                }
            ]
        }
        apply_func(Job(job_data_dict))

    get_job_func = get_job_mock if mock else get_job
    
    header_box = widgets.HBox([widgets.Label('Job Name'), widgets.Label('Progress'), widgets.Label('Status')])
    boxes = [header_box]
    progress_bars = []
    status_labels = []
    for task_name in job.tasks.names:
        progress = job.tasks.get(task_name).progress
        status = job.tasks.get(task_name).status
        progress = widgets.IntProgress(value=progress, min=0, max=100)
        status_label = widgets.Label(status)
        box = widgets.HBox([widgets.Label(task_name), progress, status_label])
        progress_bars.append(progress)
        status_labels.append(status_label)
        boxes.append(box)

    def _update_job(job_state: Job):
        job_dict = job.as_dict()
        job_dict['status'] = job_state.status
        job_dict['progress'] = job_state.progress

    def monitor(progress_bars, status_labels):
        while True:
            task_names = job.tasks.names
            for index, task_name in enumerate(task_names):
                task = job.tasks.get(task_name)
                if status_labels[index].value == "new":
                    if task.status == "new":
                        continue
                        progress_bars[index].value = task.status
                    status_labels[index].value = task.status
                elif status_labels[index].value == "cancelled" and task.status != "cancelled":
                    progress_bars[index].value = task.progress
                    status_labels[index].value = "cancelled"
                elif status_labels[index].value == "success" and task.status != "success":
                    progress_bars[index].value = task.progress
                    status_labels[index].value = "success"
                elif status_labels[index].value == "running":
                    progress_bars[index].value = task.progress
                    status_labels[index].value = task.status
            time.sleep(0.5)
            get_job_func(job, _update_job)

    job_monitor = widgets.VBox(boxes)
    monitor_thread = threading.Thread(target=monitor, args=(progress_bars, status_labels))
    display(job_monitor)
    monitor_thread.start()
