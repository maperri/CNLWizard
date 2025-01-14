from __future__ import annotations

import abc
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, TYPE_CHECKING

from cnl2asp.exception.cnl2asp_exceptions import AttributeNotFound
from cnl2asp.converter.converter_interface import Converter, EntityConverter
from cnl2asp.specification.attribute_component import AttributeComponent, ValueComponent, \
    AttributeOrigin, is_same_origin
from cnl2asp.specification.component import Component
from cnl2asp.specification.name_component import NameComponent
from cnl2asp.specification.relation_component import RelationComponent
from cnl2asp.utility.utility import Utility

if TYPE_CHECKING:
    from cnl2asp.parser.proposition_builder import PropositionBuilder


class EntityType(Enum):
    GENERIC = 0
    TIME = 1
    DATE = 2
    STEP = 3
    ANGLE = 4
    SET = 5
    LIST = 6


class EntityComponent(Component):
    def __init__(self, name: str, label: str, keys: list[AttributeComponent], attributes: list[AttributeComponent],
                 negated: bool = False, entity_type: EntityType = EntityType.GENERIC,
                 is_before: bool = False, is_after: bool = False, is_initial: bool = False,
                 is_final: bool = False, auxiliary_verb: str = ""):
        self._name = NameComponent(name)
        self.label = label
        self.keys = keys if keys else []
        self.attributes = attributes if attributes else []
        for attribute in self.attributes:
            if attribute.origin is None:
                attribute.origin = AttributeOrigin(self.get_name())
        self.negated = negated
        self.entity_type = entity_type
        self.auxiliary_verb = auxiliary_verb
        self.is_before = is_before
        self.is_after = is_after
        self.is_initial = is_initial
        self.is_final = is_final

    def label_is_key_value(self):
        if self.label and len(self.get_keys()) == 1 and self.get_keys()[0].value == Utility.NULL_VALUE:
            return True
        return False

    def set_label_as_key_value(self):
        self.set_attributes_value([AttributeComponent(self.get_keys()[0].get_name(),
                                   ValueComponent(self.label), self.get_keys()[0].origin)])

    def get_name(self):
        return str(self._name)

    def get_initialized_attributes(self) -> list[AttributeComponent]:
        res = []
        for attribute in self.get_attributes():
            if attribute.value != Utility.NULL_VALUE:
                res.append(attribute)
        return res

    def has_attribute_value(self, value: ValueComponent) -> bool:
        for attribute in self.attributes:
            if attribute.value == value:
                return True
        return False

    def convert(self, converter: Converter) -> EntityConverter:
        return converter.convert_entity(self)

    def negate(self):
        self.negated = not self.negated

    def get_entity_identifier(self):
        return self._name

    def get_keys(self) -> list[AttributeComponent]:
        return self.keys if self.keys else self.attributes

    def get_attributes(self) -> list[AttributeComponent]:
        if self.keys:
            return self.attributes
        return []

    def get_keys_and_attributes(self) -> list[AttributeComponent]:
        return self.keys + self.attributes

    def set_attributes_value(self, attributes: list[AttributeComponent], proposition: PropositionBuilder = None):
        def update_attribute(attribute, value, operations):
            attribute.value = value
            attribute.operations = operations

        def get_first_null_attribute(attributes):
            for attribute in attributes:
                if attribute.value == Utility.NULL_VALUE:
                    return attribute
            return None

        for attribute in attributes:
            if isinstance(attribute, EntityComponent):
                if not proposition:
                    raise RuntimeError('Error in compilation phase.')
                proposition.add_relations([RelationComponent(self, attribute)])
            else:
                origin = attribute.origin
                if not origin:
                    origin = AttributeOrigin(str(self.get_name()))
                matching_attributes = self.get_attributes_by_name_and_origin(attribute.get_name(), origin)
                if get_first_null_attribute(matching_attributes):
                    update_attribute(get_first_null_attribute(matching_attributes), attribute.value,
                                     attribute.operations)
                else:
                    for matching_attribute in matching_attributes:
                        update_attribute(matching_attribute, attribute.value, attribute.operations)

    def get_attributes_by_name_and_origin(self, name: str, origin: AttributeOrigin = None) -> list[AttributeComponent]:
        attributes = []
        origin = AttributeOrigin(self.get_name()) if not origin else origin
        for attribute in self.get_keys_and_attributes():
            if attribute.name_match(name) and is_same_origin(attribute.origin, origin):
                attributes.append(attribute)
        if attributes:
            return attributes
        else:
            error_msg = f'Entity \"{self.get_name()}\" do not contain attribute \"{origin} {name}\".'
            try:
                hint = self.get_attributes_by_name(name)
                error_msg += f'\nDid you mean \"{hint[0]}\"?'
            except AttributeNotFound:
                pass
            raise AttributeNotFound(error_msg)

    def get_attributes_by_name(self, name: str) -> list[AttributeComponent]:
        attributes = []
        for attribute in self.get_keys_and_attributes():
            if attribute.name_match(name):
                attributes.append(attribute)
        if attributes:
            return attributes
        raise AttributeNotFound(f'Entity \"{self.get_name()}\" do not contain attribute \"{name}\".')

    def copy(self) -> EntityComponent:
        keys = [key.copy() for key in self.keys]
        attributes = [attribute.copy() for attribute in self.attributes]
        return EntityComponent(self.get_name(), self.label, keys,
                               attributes, self.negated, self.entity_type,
                               self.is_before, self.is_after, self.is_initial, self.is_final,
                               self.auxiliary_verb)

    def get_entities(self) -> list[EntityComponent]:
        return [self]

    def get_entities_to_link_with_new_knowledge(self) -> list[EntityComponent]:
        return [self]

    def __eq__(self, other):
        if not isinstance(other, EntityComponent):
            return False
        return self._name == other._name \
               and self.label == other.label \
               and self.keys == other.keys \
               and self.attributes == other.attributes \
               and self.negated == other.negated \
               and self.entity_type == other.entity_type


