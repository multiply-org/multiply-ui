import ipywidgets as widgets
from IPython.display import display
import threading
import time

from .api import get_job
from .model import Job
from ..debug import get_debug_view


def obs_job_form(job: Job, mock=False):
    debug_view = get_debug_view()

    get_job_func = get_job
    if mock:
        @debug_view.capture(clear_output=True)
        def get_job_mock(job_state: Job, apply_func):
            debug_view.value = ''
            import time
            time.sleep(1)
            job_status = "running"
            job_progress = 0
            previous_task_succeeded = True
            task_list = []
            for job_task_name in job.tasks.names:

                task_progress = job.tasks.get(job_task_name).progress
                task_status = job.tasks.get(job_task_name).status
                if previous_task_succeeded and task_progress < 100:
                    task_progress += 5
                    task_progress = min(task_progress, 100)
                    task_status = "running"
                job_progress += task_progress
                if task_progress == 100:
                    task_status = "succeeded"
                else:
                    previous_task_succeeded = False
                task_list.append(
                    {
                        "name": job_task_name,
                        "progress": task_progress,
                        "status": task_status
                     }
                )
            print(task_list)
            if previous_task_succeeded:
                job_status = "succeeded"
            job_progress = int(job_progress / len(job.tasks.names))
            job_data_dict = {
                "id": job_state.id,
                "name": job_state.name,
                "progress": job_progress,
                "status": job_status,
                "tasks": task_list
            }
            apply_func(Job(job_data_dict))
        get_job_func = get_job_mock

    job_header_id_label = widgets.Label('Job ID')
    job_header_name_label = widgets.Label('Job Name')
    job_header_progress_label = widgets.Label('Progress')
    job_header_status_label = widgets.Label('Status')
    job_progress_bar = widgets.IntProgress(value=job.progress, min=0, max=100)
    job_status_label = widgets.Label(job.status)
    job_id_label = widgets.Label(job.id)
    job_name_label = widgets.Label(job.name)
    job_grid_box = widgets.GridBox(children=[job_header_id_label, job_header_name_label,
                                            job_header_progress_label, job_header_status_label,
                                            job_id_label, job_name_label, job_progress_bar, job_status_label],
                                    layout=widgets.Layout(
                                    width='50%',
                                    grid_template_rows='auto auto',
                                    grid_template_columns='20% 20% 40% 20%'
                                    )
                                  )
    task_header_name_label = widgets.Label('Task Name')
    task_header_progress_label = widgets.Label('Progress')
    task_header_status_label = widgets.Label('Status')
    task_gridbox_children = [task_header_name_label, task_header_progress_label, task_header_status_label]
    task_gridbox_template_rows = 'auto'
    task_progress_bars = []
    task_status_labels = []
    for task_name in job.tasks.names:
        progress = job.tasks.get(task_name).progress
        status = job.tasks.get(task_name).status
        progress = widgets.IntProgress(value=progress, min=0, max=100)
        status_label = widgets.Label(status)
        task_name_label = widgets.Label(task_name)
        task_gridbox_children.append(task_name_label)
        # noinspection PyTypeChecker
        task_gridbox_children.append(progress)
        task_gridbox_children.append(status_label)
        task_progress_bars.append(progress)
        task_status_labels.append(status_label)
        task_gridbox_template_rows = task_gridbox_template_rows + ' auto'

    task_grid_box = widgets.GridBox(children=task_gridbox_children,
                                    layout=widgets.Layout(
                                    width='50%',
                                    grid_template_rows=task_gridbox_template_rows,
                                    grid_template_columns='30% 50% 20%'
                                    )
    )
    job_monitor = widgets.VBox([job_grid_box, task_grid_box])

    def _update_job(job_state: Job):
        job.update(job_state.as_dict())

    def monitor(progress_bar, status_bar, progress_bars, status_labels):
        while True:
            progress_bar.value = job.progress
            status_bar.value = job.status
            job_task_names = job.tasks.names
            for index, job_task_name in enumerate(job_task_names):
                task = job.tasks.get(job_task_name)
                progress_bars[index].value = task.progress
                status_labels[index].value = task.status
            time.sleep(0.5)
            get_job_func(job, _update_job)

    monitor_thread = threading.Thread(target=monitor, args=(job_progress_bar, job_status_label,
                                                            task_progress_bars, task_status_labels))
    # noinspection PyTypeChecker
    display(job_monitor)
    monitor_thread.start()
