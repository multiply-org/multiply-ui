from typing import Dict, Any, List, Optional

from ..util.callapi import call_api
from ..util.schema import PropertyDef, TypeDef

URL_BASE = "http://localhost:9090/"

GET_PROC_PARAMS_URL = URL_BASE + "multiply/api/processing/parameters"


class Variable:
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def id(self) -> str:
        return self._data['id']

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def unit(self) -> Optional[str]:
        return self._data['unit']

    @property
    def description(self) -> Optional[str]:
        return self._data['description']

    def _repr_html_(self):
        return self.html_table([self])

    @classmethod
    def html_table(cls, variables: List['Variable']):
        table_header = (f"<tr>"
                        f"<th>Variable ID</th>"
                        f"<th>Name</th>"
                        f"<th>Units</th>"
                        f"<th>Description</th>"
                        f"</tr>")

        table_rows = []
        for variable in variables:
            table_rows.append(f"<tr>"
                              f"<td>{variable.id}</td>"
                              f"<td>{variable.name}</td>"
                              f"<td>{variable.unit}</td>"
                              f"<td>{variable.description}</td>"
                              f"</tr>")

        return (
            f"<table>"
            f"  {table_header}"
            f"  {''.join(table_rows)}"
            f"</table>"
        )


class Variables:
    def __init__(self, variables: Dict[str, Variable]):
        self._variables = variables

    @property
    def ids(self) -> List[str]:
        return list(self._variables.keys())

    def get(self, var_id: str) -> Variable:
        return self._variables[var_id]

    def _repr_html_(self):
        return Variable.html_table(list(self._variables.values()))


class ForwardModel:
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def id(self) -> str:
        return self._data['id']

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def description(self) -> Optional[str]:
        return self._data['description']

    @property
    def model_authors(self) -> Optional[str]:
        return self._data['modelAuthors']

    @property
    def model_url(self) -> Optional[str]:
        return self._data['modelurl']

    def _repr_html_(self):
        return self.html_table([self])

    @classmethod
    def html_table(cls, items: List['ForwardModel']):
        table_header = (f"<tr>"
                        f"<th>Forward Model ID</th>"
                        f"<th>Name</th>"
                        f"<th>Description</th>"
                        f"<th>Author(s)</th>"
                        f"<th>URL</th>"
                        f"</tr>")

        table_rows = []
        for item in items:
            table_rows.append(f"<tr>"
                              f"<td>{item.id}</td>"
                              f"<td>{item.name}</td>"
                              f"<td>{item.description}</td>"
                              f"<td>{item.model_authors}</td>"
                              f"<td>{item.model_url}</td>"
                              f"</tr>")

        return (
            f"<table>"
            f"  {table_header}"
            f"  {''.join(table_rows)}"
            f"</table>"
        )


class ForwardModels:
    def __init__(self, forward_models: Dict[str, ForwardModel]):
        self._forward_models = forward_models

    @property
    def ids(self) -> List[str]:
        return list(self._forward_models.keys())

    def get(self, fm_id: str) -> ForwardModel:
        return self._forward_models[fm_id]

    def _repr_html_(self):
        return ForwardModel.html_table(list(self._forward_models.values()))


class ProcessingParameters:

    @classmethod
    def load(cls):
        def apply_func(json_obj: Dict) -> ProcessingParameters:
            return ProcessingParameters(json_obj)

        return call_api(GET_PROC_PARAMS_URL, apply_func)

    def __init__(self, raw_data):

        prefix = 'processing parameters: '
        PARAMETERS_TYPE.validate(raw_data, prefix=prefix)

        input_types = raw_data['inputTypes']
        forward_models = raw_data['forwardModels']
        variables = {variable['id']: variable for variable in raw_data['variables']}

        for forward_model in forward_models:
            forward_model_variable_ids = forward_model['variables']
            for forward_model_variable_id in forward_model_variable_ids:
                if forward_model_variable_id not in variables:
                    raise ValueError(f'{prefix}undescribed variable {forward_model_variable_id!r} '
                                     f'found in forward model {forward_model["name"]}')
                variable = variables[forward_model_variable_id]
                if 'forwardModels' not in variable:
                    variable['forwardModels'] = []
                variable['forwardModels'].append(forward_model['id'])

        self._input_types = {input_type['id']: input_type for input_type in input_types}
        self._forward_models = ForwardModels({forward_model['id']: ForwardModel(forward_model)
                                              for forward_model in forward_models})
        self._variables = Variables({variable['id']: Variable(variable)
                                     for variable in variables.values()})

    @property
    def variables(self) -> Variables:
        return self._variables

    @property
    def forward_models(self) -> ForwardModels:
        return self._forward_models


INPUT_TYPES_TYPE = TypeDef(dict, properties=[
    PropertyDef('id', TypeDef(str)),
    PropertyDef('name', TypeDef(str)),
    PropertyDef('timeRange', TypeDef(list)),
])

VARIABLE_TYPE = TypeDef(dict, properties=[
    PropertyDef('id', TypeDef(str)),
    PropertyDef('name', TypeDef(str)),
    PropertyDef('unit', TypeDef(str, optional=True)),
    PropertyDef('description', TypeDef(str, optional=True)),
    PropertyDef('valueRange', TypeDef(str, optional=True)),
    PropertyDef('applications', TypeDef(list, optional=True, item_type=TypeDef(str))),
])

FORWARD_MODEL_TYPE = TypeDef(dict, properties=[
    PropertyDef('id', TypeDef(str)),
    PropertyDef('name', TypeDef(str)),
    PropertyDef('description', TypeDef(str, optional=True)),
    PropertyDef('modelAuthor', TypeDef(str, optional=True)),
    PropertyDef('modelurl', TypeDef(str, optional=True)),
    PropertyDef('inputType', TypeDef(str)),
    PropertyDef('variables', TypeDef(list, item_type=TypeDef(str))),
])

PARAMETERS_TYPE = TypeDef(dict, properties=[
    PropertyDef("inputTypes", TypeDef(list, item_type=INPUT_TYPES_TYPE)),
    PropertyDef("variables", TypeDef(list, item_type=VARIABLE_TYPE)),
    PropertyDef("forwardModels", TypeDef(list, item_type=FORWARD_MODEL_TYPE)),
])
