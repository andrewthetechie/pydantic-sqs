"""Module containing the main base classes"""
from enum import Enum
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from ipaddress import IPv6Address
from ipaddress import IPv6Network
from uuid import UUID

from pydantic import BaseModel
from pydantic.fields import SHAPE_DEFAULTDICT
from pydantic.fields import SHAPE_DICT
from pydantic.fields import SHAPE_FROZENSET
from pydantic.fields import SHAPE_LIST
from pydantic.fields import SHAPE_MAPPING
from pydantic.fields import SHAPE_SEQUENCE
from pydantic.fields import SHAPE_SET
from pydantic.fields import SHAPE_TUPLE
from pydantic.fields import SHAPE_TUPLE_ELLIPSIS

# JSON_DUMP_SHAPES are object types that are serialized to JSON using json.dumps
JSON_DUMP_SHAPES = (
    SHAPE_LIST,
    SHAPE_SET,
    SHAPE_MAPPING,
    SHAPE_TUPLE,
    SHAPE_TUPLE_ELLIPSIS,
    SHAPE_SEQUENCE,
    SHAPE_FROZENSET,
    SHAPE_DICT,
    SHAPE_DEFAULTDICT,
    Enum,
)

# STR_DUMP_SHAPES are object types that are serialized to strings using str(obj)
# They are stored in redis as strings and rely on pydantic to deserialize them
STR_DUMP_SHAPES = (IPv4Address, IPv4Network, IPv6Address, IPv6Network, UUID)


class _AbstractQueue(BaseModel):
    """
    An abstract class of a queue
    """

    queue_url: str
    aws_region: str = "us-east-1"

    class Config:
        """Pydantic schema config for _AbstractStore"""

        arbitrary_types_allowed = True
        orm_mode = True


class _AbstractModel(BaseModel):
    """
    An abstract class to help with typings for Model class
    """

    _queue: _AbstractQueue
