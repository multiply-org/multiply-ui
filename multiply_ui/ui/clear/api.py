from enum import Enum
from typing import List
from ...util.callapi import call_api

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

URL_BASE = "http://localhost:9090/"

CLEAR_URL = URL_BASE + "multiply/api/clear"


class ClearanceType(Enum):
    CACHE = 0
    WORKING_DIRS = 1
    AUXILIARY_DATA = 2
    ARCHIVED_DATA = 3


def clear(clearance_type: ClearanceType):
    type_dict = {}
    if clearance_type == ClearanceType.CACHE:
        type_dict['clearance'] = 'cache'
    if clearance_type == ClearanceType.WORKING_DIRS:
        type_dict['clearance'] = 'working'
    if clearance_type == ClearanceType.AUXILIARY_DATA:
        type_dict['clearance'] = 'aux'
    if clearance_type == ClearanceType.ARCHIVED_DATA:
        type_dict['clearance'] = 'archive'
    return call_api(CLEAR_URL, params=type_dict)
