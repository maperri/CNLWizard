from __future__ import annotations

from enum import Enum

from cnl2asp.specification.attribute_component import AttributeComponent
from cnl2asp.specification.component import Component
from cnl2asp.converter.converter_interface import Converter, AggregateConverter
from cnl2asp.specification.entity_component import EntityComponent


class AggregateOperation(Enum):
    COUNT = 0
    SUM = 1
    MAX = 2
    MIN = 3

