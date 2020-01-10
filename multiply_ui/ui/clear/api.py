from enum import Enum
from typing import List
from ...util.callapi import call_api

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

URL_BASE = "http://localhost:9090/"

CLEAR_URL = URL_BASE + "multiply/api/clear/{}"


class ClearanceType(Enum):
    CACHE = 0
    WORKING_DIRS = 1
    AUXILIARY_DATA = 2
    ARCHIVED_DATA = 3


def clear(clearance_type: ClearanceType):
    if clearance_type == ClearanceType.CACHE:
        clearance = 'cache'
    elif clearance_type == ClearanceType.WORKING_DIRS:
        clearance = 'working'
    elif clearance_type == ClearanceType.AUXILIARY_DATA:
        clearance = 'aux'
    elif clearance_type == ClearanceType.ARCHIVED_DATA:
        clearance = 'archive'
    else:
        return
    return call_api(CLEAR_URL.format(clearance))
