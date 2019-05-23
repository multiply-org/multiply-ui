from ..params.model import TIME_RANGE_TYPE
from ...util.schema import PropertyDef, TypeDef

PRODUCT_IDENTIFIERS_TYPE = TypeDef(dict,
                                   key_type=TypeDef(str),
                                   item_type=TypeDef(list, item_type=TypeDef(str)))

INPUT_REQUEST_TYPE = TypeDef(object, properties=[
    PropertyDef('name', TypeDef(str)),
    PropertyDef('bbox', TypeDef(str)),
    PropertyDef('timeRange', TIME_RANGE_TYPE),
    PropertyDef('inputTypes', TypeDef(list, item_type=TypeDef(str))),
])

PROCESSING_REQUEST_TYPE = TypeDef(object, properties=[
    PropertyDef('name', TypeDef(str)),
    PropertyDef('bbox', TypeDef(str)),
    PropertyDef('timeRange', TIME_RANGE_TYPE),
    PropertyDef('inputTypes', TypeDef(list, item_type=TypeDef(str))),
    PropertyDef('productIdentifiers', PRODUCT_IDENTIFIERS_TYPE),
])
