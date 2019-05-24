import datetime
from typing import List
import ipywidgets as widgets
from IPython.display import display
import threading

from multiply_ui.ui.req.model import InputRequest, ProcessingRequest
from multiply_ui.ui.job.model import Job
# from .api import fetch_inputs

def job_monitor(job: Job):
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

    job_monitor = widgets.VBox(boxes)
    monitor_thread = threading.Thread(target=monitor, args=(progress_bars, status_labels))
    display(job_monitor)
    monitor_thread.start()
