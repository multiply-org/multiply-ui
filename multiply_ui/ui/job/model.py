from typing import Dict, Any, List

from ...util.html import html_table
from ...util.schema import PropertyDef, TypeDef

TASK_TYPE = TypeDef(object, properties=[
    PropertyDef('name', TypeDef(str)),
    PropertyDef('progress', TypeDef(int)),
    PropertyDef('status', TypeDef(str)),
])

JOB_TYPE = TypeDef(object, properties=[
    PropertyDef("name", TypeDef(str)),
    PropertyDef("progress", TypeDef(int)),
    PropertyDef("status", TypeDef(str)),
    PropertyDef("tasks", TypeDef(list, item_type=TASK_TYPE)),
])


class Task:
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def progress(self) -> int:
        return self._data['progress']

    @property
    def status(self) -> str:
        return self._data['status']

    def _repr_html_(self):
        return self.html_table([self])

    @classmethod
    def html_table(cls, items: List['Task'], title=None):
        def data_row(item: Task):
            return [item.name, item.progress, item.status]

        return html_table(list(map(data_row, items)),
                          header_row=['Name', 'Progress', 'Status'],
                          title=title)


class Tasks:
    def __init__(self, tasks: Dict[str, Task]):
        self._tasks = tasks

    @property
    def names(self) -> List[str]:
        return list(self._tasks.keys())

    def get(self, it_id: str) -> Task:
        return self._tasks[it_id]

    def _repr_html_(self):
        return Task.html_table(list(self._tasks.values()), title="Tasks")


class Job:

    def __init__(self, raw_data):
        prefix = 'job: '
        JOB_TYPE.validate(raw_data, prefix=prefix)

        self._name = raw_data['name']
        self._progress = raw_data['progress']
        self._status = raw_data['status']
        tasks = raw_data['tasks']
        self._tasks = Tasks({task['name']: Task(task) for task in tasks})

    @property
    def name(self) -> str:
        return self._name

    @property
    def progress(self) -> int:
        return self._progress

    @property
    def status(self) -> int:
        return self._status

    @property
    def tasks(self) -> Tasks:
        return self._tasks
