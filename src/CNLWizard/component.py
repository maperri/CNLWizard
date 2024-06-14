from __future__ import annotations

from abc import ABC, abstractmethod
from CNLWizard.CNLWizard import Cnl, CNAME


class Component(ABC):
    dependencies: list[Component] = []

    @abstractmethod
    def compile(self, cnl: Cnl):
        """Add grammar rule(s) and function(s) to CNL"""


class Attribute(Component):
    def compile(self, cnl: Cnl) -> [str, str]:
        @cnl.rule('"with" CNAME "equal to" (CNAME | NUMBER)')
        def attribute(name, attribute_value):
            return name, attribute_value

        cnl.support_rule('attributes', 'attribute', concat=',')


class Entity(Component):
    def compile(self, cnl: Cnl) -> [str, str]:
        @cnl.rule('("a" | "an")? CNAME attributes', dependencies=['attributes'])
        def entity(name, attributes):
            try:
                entity = Cnl.signatures[name]
                for name, value in attributes:
                    entity.fields[name] = value
                return entity
            except KeyError:
                return None


class MathOperation(Component):
    def __init__(self):
        self.operators = {
            'sum': "+",
            'difference': "-",
            'division': "/",
            'multiplication': "*"}

    def compile(self, cnl: Cnl):
        cnl.support_rule('math_operator', self.operators)

        @cnl.rule('"the" math_operator "between" operand "and" operand', dependencies=['operand'])
        def math_operation(math_operator, *args):
            if isinstance(math_operator, str):
                return math_operator.join(args)
            elif callable(math_operator):
                return math_operator(*args)

    def __setitem__(self, key, value):
        self.operators[key] = value
