import ipywidgets as widgets
import threading
import time

from IPython.display import display
from typing import Optional

from .api import cancel, get_job
from .model import Job, JOBS
from ..debug import get_debug_view
from ..info import InfoComponent


def obs_job_form(job: Job, mock=False):
    get_job_func = _get_job_func(job, mock)

    info = InfoComponent()
    job_header_id_label = widgets.HTML(value = f"<b>Job ID</b>")
    job_header_name_label = widgets.HTML(value = f"<b>Job Name</b>")
    job_header_progress_label = widgets.HTML(value = f"<b>Progress</b>")
    job_header_status_label = widgets.HTML(value = f"<b>Status</b>")
    job_progress_bar = widgets.IntProgress(value=job.progress, min=0, max=100)
    job_status_label = widgets.Label(job.status)
    job_id_label = widgets.Label(job.id)
    job_name_label = widgets.Label(job.name)
    job_cancel_button = widgets.Button(description="Cancel", icon="times-circle")
    job_cancel_button.on_click(_get_handle_cancel_button_clicked(job.id, info.message_func, mock))
    job_grid_box = widgets.GridBox(children=[job_header_id_label, job_header_name_label,
                                             job_header_progress_label, job_header_status_label, job_cancel_button,
                                             job_id_label, job_name_label, job_progress_bar, job_status_label,
                                             widgets.Label()],
                                   layout=widgets.Layout(
                                       width='100%',
                                       grid_template_rows='auto auto',
                                       grid_template_columns = '22% 21% 27% 10% 20%'
                                   )
                                   )
    task_header_name_label = widgets.HTML(value = f"<b>Task</b>")
    task_header_progress_label = widgets.HTML(value = f"<b>Progress</b>")
    task_header_status_label = widgets.HTML(value = f"<b>Status</b>")

    task_gridbox_children = widgets.GridBox(
        children=[task_header_name_label, task_header_progress_label, task_header_status_label],
        layout=widgets.Layout(grid_template_columns='43% 43% 14%')
    )

    info_displayed = []

    def _toggle_info_display(task_details, details_button, task_id, task_logs):
        task_details.clear_output()
        if details_button.icon == "chevron-circle-down":
            task_details.layout = {'border': '1px solid black'}
            info_displayed.append(task_id)
            with task_details:
                for log in task_logs:
                    print(log)
            details_button.icon = "chevron-circle-up"
        else:
            task_details.layout = {}
            info_displayed.remove(task_id)
            details_button.icon = "chevron-circle-down"

    def _get_details_button(_func, task_details, task_id, task_logs):
        details_button = widgets.Button(icon="chevron-circle-down", tooltip="Show processing details",
                                        layout=widgets.Layout(width='80%'))

        def _apply_func(b):
            _func(task_details, details_button, task_id, task_logs)

        details_button.on_click(_apply_func)
        if task_id not in info_displayed:
            details_button.icon = "chevron-circle-down"
            task_details.layout = {}
        else:
            details_button.icon = "chevron-circle-up"
            task_details.layout = {'border': '1px solid black'}
            for line in task_logs:
                task_details.append_stdout(f'{line}\n')

        return details_button

    def _get_tasks_gridbox(grid_job):
        gridbox_children = [task_gridbox_children]
        task_details_list = []
        for task_name in grid_job.tasks.names:
            progress = grid_job.tasks.get(task_name).progress
            status = grid_job.tasks.get(task_name).status
            progress = widgets.IntProgress(value=progress, min=0, max=100)
            status_label = widgets.Label(status)
            task_name_label = widgets.Label(task_name)
            task_details = widgets.Output()
            logs = grid_job.tasks.get(task_name).logs
            details_button = _get_details_button(_toggle_info_display, task_details, task_name, logs)
            task_details_list.append(task_details)
            row_children = [task_name_label, progress, status_label, details_button]
            row_box = widgets.GridBox(children=row_children,
                                      layout=widgets.Layout(grid_template_columns='43% 43% 9% 5%'))
            gridbox_children.append(row_box)
            gridbox_children.append(task_details)
        grid_box = widgets.GridBox(children=gridbox_children, layout=widgets.Layout(width='100%'))
        return grid_box

    tasks_gridbox = _get_tasks_gridbox(job)
    info = InfoComponent()
    job_monitor = widgets.VBox([job_grid_box, tasks_gridbox, info.as_widget(100)])

    def monitor(progress_bar, status_bar, cancel_button):
        while job.status not in ['succeeded', 'cancelled', 'failed']:
            time.sleep(10)
            job_state = get_job_func(job, info.message_func)
            if job_state is not None:
                _update_job(job, job_state)
            progress_bar.value = job.progress
            status_bar.value = job.status
            grid_box = _get_tasks_gridbox(job)
            if job.status != 'new' and job.status != 'running':
                cancel_button.disabled = True
            job_monitor.children = ([job_grid_box, grid_box, info.as_widget(100)])


    monitor_components = (job_progress_bar, job_status_label, job_cancel_button)
    _monitor(monitor, job_monitor, monitor_components)


def _get_handle_cancel_button_clicked(job_id: str, message_func, mock=False):
    debug_view = get_debug_view()

    @debug_view.capture(clear_output=True)
    def handle_cancel_button_clicked(*args, **kwargs):
        cancel(job_id, mock=mock, message_func=message_func)

    return handle_cancel_button_clicked


def obs_jobs_form(mock=False):
    info = InfoComponent()
    job_header_id_label = widgets.HTML(value = f"<b>Job ID</b>")
    job_header_name_label = widgets.HTML(value = f"<b>Job Name</b>")
    job_header_progress_label = widgets.HTML(value = f"<b>Progress</b>")
    job_header_status_label = widgets.HTML(value = f"<b>Status</b>")
    jobs_box_children = [job_header_id_label, job_header_name_label, job_header_progress_label, job_header_status_label,
                         widgets.Label()]
    grid_template_rows = 'auto'
    job_components = {}
    for job in JOBS.values():
        job_progress_bar = widgets.IntProgress(value=job.progress, min=0, max=100)
        job_status_label = widgets.Label(job.status)
        job_id_label = widgets.Label(job.id)
        job_name_label = widgets.Label(job.name)
        job_cancel_button = widgets.Button(description="Cancel", icon="times-circle")
        job_cancel_button.on_click(_get_handle_cancel_button_clicked(job.id, info.message_func, mock))
        jobs_box_children.append(job_id_label)
        jobs_box_children.append(job_name_label)
        jobs_box_children.append(job_progress_bar)
        jobs_box_children.append(job_status_label)
        jobs_box_children.append(job_cancel_button)
        grid_template_rows = grid_template_rows + ' auto'
        job_components[f'{job.id}'] = (job_progress_bar, job_status_label, job_cancel_button, _get_job_func(job, mock), job)
    jobs_monitor_component = widgets.GridBox(children=jobs_box_children,
                                    layout=widgets.Layout(
                                        width='100%',
                                        grid_template_rows=grid_template_rows,
                                        grid_template_columns='10% 20% 40% 10% 20%'
                                    )
                                    )
    jobs_full_component = widgets.VBox([jobs_monitor_component, info.as_widget(100)])

    def jobs_monitor_func(components, empty):
        at_least_one_job_unfinished = True
        while at_least_one_job_unfinished:
            at_least_one_job_unfinished = False
            for progress_bar, status_label, cancel_button, job_func, component_job in components.values():
                job_state = job_func(component_job, info.message_func)
                if job_state is not None:
                    _update_job(component_job, job_state)
                progress_bar.value = component_job.progress
                status_label.value = component_job.status
                if component_job.status != 'new' and component_job.status != 'running':
                    cancel_button.disabled = True
                if component_job.status not in ['succeeded', 'cancelled', 'failed']:
                    at_least_one_job_unfinished = True
            time.sleep(10)

    _monitor(jobs_monitor_func, jobs_full_component, (job_components, None))


def _get_job_func(job: Job, mock=False):
    if not mock:
        return get_job

    debug_view = get_debug_view()

    @debug_view.capture(clear_output=True)
    def get_job_mock(job_state: Job, message_func) -> Optional[Job]:
        debug_view.value = ''
        message_func('Retrieving job status ...')
        import time
        time.sleep(3)
        if job.status != "new" and job.status != "running":
            return None
        job_status = "running"
        job_progress = 0
        previous_task_succeeded = True
        task_list = []
        for job_task_name in job.tasks.names:
            task_progress = job.tasks.get(job_task_name).progress
            task_status = job.tasks.get(job_task_name).status
            task_logs = job.tasks.get(job_task_name).logs
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
                    "status": task_status,
                    "logs": task_logs
                }
            )
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
        return Job(job_data_dict)

    return get_job_mock


def _update_job(job: Job, job_state: Job):
    job.update(job_state.as_dict())


def _monitor(monitorFunc, monitorComponent, monitorComponents):
    monitor_thread = threading.Thread(target=monitorFunc, args=monitorComponents)
    # noinspection PyTypeChecker
    display(monitorComponent)
    monitor_thread.start()
