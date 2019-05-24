from typing import Dict, Any, List, Optional, Tuple

from ...util.html import html_table, html_element
from ...util.schema import PropertyDef, TypeDef

TIME_RANGE_TYPE = TypeDef(list, item_type=TypeDef(str, optional=True), num_items=2)

INPUT_TYPES_TYPE = TypeDef(object, properties=[
    PropertyDef('id', TypeDef(str)),
    PropertyDef('name', TypeDef(str)),
    PropertyDef('timeRange', TIME_RANGE_TYPE),
])

VARIABLE_TYPE = TypeDef(object, properties=[
    PropertyDef('id', TypeDef(str)),
    PropertyDef('name', TypeDef(str)),
    PropertyDef('unit', TypeDef(str, optional=True)),
    PropertyDef('description', TypeDef(str, optional=True)),
    PropertyDef('valueRange', TypeDef(str, optional=True)),
    PropertyDef('applications', TypeDef(list, optional=True, item_type=TypeDef(str))),
])

FORWARD_MODEL_TYPE = TypeDef(object, properties=[
    PropertyDef('id', TypeDef(str)),
    PropertyDef('name', TypeDef(str)),
    PropertyDef('description', TypeDef(str, optional=True)),
    PropertyDef('modelAuthor', TypeDef(str, optional=True)),
    PropertyDef('modelurl', TypeDef(str, optional=True)),
    PropertyDef('inputType', TypeDef(str)),
    PropertyDef('variables', TypeDef(list, item_type=TypeDef(str))),
])

PARAMETERS_TYPE = TypeDef(object, properties=[
    PropertyDef("inputTypes", TypeDef(list, item_type=INPUT_TYPES_TYPE)),
    PropertyDef("variables", TypeDef(list, item_type=VARIABLE_TYPE)),
    PropertyDef("forwardModels", TypeDef(list, item_type=FORWARD_MODEL_TYPE)),
])


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
    def html_table(cls, variables: List['Variable'], title=None):
        def data_row(variable: Variable):
            return [variable.id, variable.name, variable.unit, variable.description]

        data_rows = list(map(data_row, variables))
        return html_table(data_rows, header_row=['Id', 'Name', 'Units', 'Description'], title=title)


class Variables:
    def __init__(self, variables: Dict[str, Variable]):
        self._variables = variables

    @property
    def ids(self) -> List[str]:
        return list(self._variables.keys())

    def get(self, var_id: str) -> Variable:
        return self._variables[var_id]

    def _repr_html_(self):
        return Variable.html_table(list(self._variables.values()), title='Variables')


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
        return self._data['modelAuthor']

    @property
    def model_url(self) -> Optional[str]:
        return self._data['modelurl']

    def _repr_html_(self):
        return self.html_table([self])

    @classmethod
    def html_table(cls, items: List['ForwardModel'], title=None):
        def anchor(item: str):
            return html_element('a', att=dict(href=item), value='More...')

        def data_row(item: ForwardModel):
            return [item.id, item.name, item.description, item.model_authors, item.model_url]

        return html_table(list(map(data_row, items)),
                          header_row=['Id', 'Name', 'Description', 'Author(s)', ''],
                          title=title,
                          col_converter={4: anchor})


class ForwardModels:
    def __init__(self, forward_models: Dict[str, ForwardModel]):
        self._forward_models = forward_models

    @property
    def ids(self) -> List[str]:
        return list(self._forward_models.keys())

    def get(self, fm_id: str) -> ForwardModel:
        return self._forward_models[fm_id]

    def _repr_html_(self):
        return ForwardModel.html_table(list(self._forward_models.values()), title="Forward Models")


class InputType:
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def id(self) -> str:
        return self._data['id']

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def time_range(self) -> Tuple[Optional[str], Optional[str]]:
        start, stop = self._data['timeRange']
        return start, stop

    def _repr_html_(self):
        return self.html_table([self])

    @classmethod
    def html_table(cls, items: List['InputType'], title=None):
        def data_row(item: InputType):
            return [item.id, item.name, item.time_range]

        return html_table(list(map(data_row, items)),
                          header_row=['Id', 'Name', 'Time Range'],
                          title=title)


class InputTypes:
    def __init__(self, input_types: Dict[str, InputType]):
        self._input_types = input_types

    @property
    def ids(self) -> List[str]:
        return list(self._input_types.keys())

    def get(self, it_id: str) -> InputType:
        return self._input_types[it_id]

    def _repr_html_(self):
        return InputType.html_table(list(self._input_types.values()), title="Input Types")


class ProcessingParameters:

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

        self._input_types = InputTypes({input_type['id']: InputType(input_type) for input_type in input_types})
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

    @property
    def input_types(self) -> InputTypes:
        return self._input_types
