from typing import Dict, Any, Tuple, Optional, List

from ..params.model import TIME_RANGE_TYPE
from ...util.html import html_element, html_table
from ...util.schema import PropertyDef, TypeDef

FORWARD_MODEL_TYPE = TypeDef(object, properties=[PropertyDef('name', TypeDef(str)),
                                                 PropertyDef('type', TypeDef(str)),
                                                 PropertyDef('modelDataType', TypeDef(str)),
                                                 PropertyDef('requiredPriors', TypeDef(list, item_type=TypeDef(str))),
                                                 PropertyDef('outputParameters', TypeDef(list, item_type=TypeDef(str)))
                                                 ])

USER_PRIOR_TYPE = TypeDef(object, properties=[PropertyDef('name', TypeDef(str)),
                                              PropertyDef('mu', TypeDef(float, optional=True)),
                                              PropertyDef('unc', TypeDef(float, optional=True))
])

INPUT_IDENTIFIERS_TYPE = TypeDef(dict,
                                 key_type=TypeDef(str),
                                 item_type=TypeDef(list, item_type=TypeDef(str)))

INPUT_REQUEST_TYPE = TypeDef(object, properties=[
    PropertyDef('name', TypeDef(str)),
    PropertyDef('bbox', TypeDef(str)),
    PropertyDef('timeRange', TIME_RANGE_TYPE),
    PropertyDef('timeStep', TypeDef(int)),
    PropertyDef('timeStepUnit', TypeDef(str)),
    PropertyDef('spatialResolution', TypeDef(int)),
    PropertyDef('inputTypes', TypeDef(list, item_type=TypeDef(str))),
    PropertyDef('forwardModels', TypeDef(list, item_type=FORWARD_MODEL_TYPE)),
    PropertyDef('userPriors', TypeDef(list, item_type=USER_PRIOR_TYPE))
])

PROCESSING_REQUEST_TYPE = TypeDef(object, properties=[
    PropertyDef('name', TypeDef(str)),
    PropertyDef('bbox', TypeDef(str)),
    PropertyDef('timeRange', TIME_RANGE_TYPE),
    PropertyDef('timeStep', TypeDef(int)),
    PropertyDef('timeStepUnit', TypeDef(str)),
    PropertyDef('spatialResolution', TypeDef(int)),
    PropertyDef('inputTypes', TypeDef(list, item_type=TypeDef(str))),
    PropertyDef('inputIdentifiers', INPUT_IDENTIFIERS_TYPE),
    PropertyDef('forwardModels', TypeDef(list, item_type=FORWARD_MODEL_TYPE)),
    PropertyDef('userPriors', TypeDef(list, item_type=USER_PRIOR_TYPE))
])


class InputIdentifiers:
    def __init__(self, data: Dict):
        INPUT_IDENTIFIERS_TYPE.validate(data)
        self._data = data

    def as_dict(self) -> Dict:
        return dict(self._data)

    def _repr_html_(self):
        data_rows = []
        for input_type, prod_ids in self._data.items():
            for prod_id in prod_ids:
                data_rows.append([input_type, prod_id])
        return html_table(data_rows, header_row=['Type', 'Identifier'], title='Inputs')


class InputRequestMixin:

    @property
    def name(self) -> str:
        # noinspection PyUnresolvedReferences
        return self._data['name']

    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        # noinspection PyUnresolvedReferences
        x1, y1, x2, y2 = tuple(map(float, self._data['bbox'].split(',')))
        return x1, y1, x2, y2

    @property
    def spatialResolution(self) -> int:
        # noinspection PyUnresolvedReferences
        return self._data['spatialResolution']

    @property
    def time_range(self) -> Tuple[Optional[str], Optional[str]]:
        # noinspection PyUnresolvedReferences
        start, stop = self._data['timeRange']
        return start, stop

    @property
    def time_step(self) -> int:
        # noinspection PyUnresolvedReferences
        return self._data['timeStep']

    @property
    def time_step_unit(self) -> str:
        # noinspection PyUnresolvedReferences
        return self._data['timeStepUnit']

    @property
    def input_types(self) -> List[str]:
        # noinspection PyUnresolvedReferences
        return self._data['inputTypes']

    @property
    def parameters(self) -> List[str]:
        # noinspection PyUnresolvedReferences
        return self._data['parameters']

    @property
    def forward_models(self) -> List[Dict]:
        # noinspection PyUnresolvedReferences
        return self._data['forwardModels']

    @property
    def user_priors(self) -> List[Dict]:
        return self._data['userPriors']

    def as_dict(self) -> Dict:
        # noinspection PyUnresolvedReferences
        return dict(self._data)

    def _repr_html_(self):
        # TODO: make HTML look nice
        parameters = []
        models = []
        for model in self.forward_models:
            for param in model['outputParameters']:
                if param not in parameters:
                    parameters.append(param)
            models.append(model['name'])
        user_prior_names = []
        for user_prior in self.user_priors:
            user_prior_names.append(user_prior['name'])
        return f'<p>' \
               f'Name: {self.name}<br/>' \
               f'Time range: {self.time_range}<br/>' \
               f'Time step: {self.time_step} {self.time_step_unit}<br/>' \
               f'Region box: {self.bbox}<br/>' \
               f'Spatial resolution in m: {self.spatialResolution}<br/>' \
               f'Input types: {", ".join(self.input_types)}<br/>' \
               f'Parameters: {", ".join(parameters)}<br/>' \
               f'Forward models: {", ".join(models)}<br/>' \
               f'User priors: {", ".join(user_prior_names)}' \
               f'</p>'


class InputRequest(InputRequestMixin):
    def __init__(self, data: Dict[str, Any]):
        INPUT_REQUEST_TYPE.validate(data)
        self._data = data


class ProcessingRequest(InputRequestMixin):
    def __init__(self, data: Dict[str, Any] = None):
        PROCESSING_REQUEST_TYPE.validate(data)
        self._data = data

    @property
    def has_inputs(self) -> bool:
        return 'inputIdentifiers' in self._data

    @property
    def inputs(self) -> InputIdentifiers:
        if not self.has_inputs:
            return InputIdentifiers({})
        return InputIdentifiers(self._data['inputIdentifiers'])

    def submit(self, job_var_name: str, mock=False):
        # TODO: test me, I have never been tested!
        from ..job.api import submit_processing_request
        import IPython

        job = submit_processing_request(self, mock=mock)
        if job is not None:
            print(f'Job is being executed and a job proxy object has been assigned to variable {job_var_name}.')
            ipython = IPython.get_ipython()
            ipython.push({job_var_name: job})

    def as_dict(self):
        return dict(self._data)

    def _repr_html_(self):
        # TODO: make HTML look nice
        input_request_html = super()._repr_html_()
        if self.has_inputs:
            # noinspection PyProtectedMember
            input_identifiers_html = self.inputs._repr_html_()
            input_request_html = html_element('div', value=input_request_html + input_identifiers_html)
        return input_request_html
