from typing import Any, Type, List, Optional


class TypeDef:
    def __init__(self,
                 data_type: Type[Any] = str,
                 optional: bool = False,
                 item_type: 'TypeDef' = None,
                 properties: List['PropertyDef'] = None):
        self._data_type = data_type
        self._optional = optional
        self._item_type = item_type
        self._properties = properties

    @property
    def data_type(self) -> Type[Any]:
        return self._data_type

    @property
    def optional(self) -> bool:
        return self.optional

    @property
    def item_type(self) -> Optional['TypeDef']:
        return self._item_type

    @property
    def properties(self) -> Optional[List['PropertyDef']]:
        return self._properties

    def validate(self, value: Any, ctx: str = ''):

        if value is None and not self._optional:
            raise ValueError(f'{ctx}value is not optional, but found null')

        if not isinstance(value, self._data_type):
            raise ValueError(f'{ctx}value is expected to have type {self._data_type.__name__}, '
                             f'but found {type(value).__name__}')

        if isinstance(value, list) and self._item_type is not None:
            self._validate_list(value, ctx)
        elif isinstance(value, dict) and self._properties is not None:
            self._validate_dict(value, ctx)

    def _validate_list(self, value, ctx):
        index = 0
        for item in value:
            self._item_type.validate(item, ctx=ctx + f'index {index}: ')
            index += 1

    def _validate_dict(self, value, ctx):

        for p in self._properties:
            if p.name not in value and not p.optional:
                raise ValueError(f'{ctx}missing property "{p.name}"')
            p.validate(value[p.name], ctx=ctx + f'property "{p.name}": ')

        illegal_property_names = set(value.keys()).difference(set(p.name for p in self._properties))
        if len(illegal_property_names) == 1:
            raise ValueError(f'{ctx}unexpected property "{next(list(illegal_property_names))}" found ')
        elif len(illegal_property_names) > 1:
            raise ValueError(f'{ctx}unexpected properties found: {list(illegal_property_names)!r}')


class PropertyDef:
    def __init__(self, name: str, prop_type: TypeDef):
        self._name = name
        self._type = prop_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def data_type(self) -> Type[Any]:
        return self._type.data_type

    @property
    def optional(self) -> bool:
        return self._type.optional

    @property
    def item_type(self) -> Optional['TypeDef']:
        return self._type.item_type

    @property
    def properties(self) -> Optional[List['PropertyDef']]:
        return self._type.properties

    def validate(self, value: Any, ctx: str = ''):
        self._type.validate(value, ctx=ctx)
