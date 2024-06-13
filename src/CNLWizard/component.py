from __future__ import annotations

from abc import ABC, abstractmethod
from CNLWizard.CNLWizard import Cnl, CNAME


class Component(ABC):
    dependencies: list[Component] = []

    @staticmethod
    @abstractmethod
    def grammar_rule(cnl: Cnl):
        """Add the grammar rule to CNL"""

    @staticmethod
    @abstractmethod
    def compile(*arg, **args):
        """Code to execute to compile the grammar rule"""


class Attribute(Component):

    @staticmethod
    def grammar_rule(cnl: Cnl) -> [str, str]:
        cnl.support_rule('attribute', '"with" CNAME "equal to" (CNAME | NUMBER)')
        cnl.support_rule('attributes', 'attribute', concat=',')

    @staticmethod
    def compile(name, attribute_value):
        return name, attribute_value


class Entity(Component):
    dependencies = [Attribute]

    @staticmethod
    def grammar_rule(cnl) -> [str, str]:
        cnl.support_rule('entity', '("a" | "an")? CNAME attributes')

    @staticmethod
    def compile(name, attributes):
        entity = Cnl.signatures[name]
        for name, value in attributes:
            entity.fields[name] = value
        return entity
