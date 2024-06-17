from __future__ import annotations

from abc import ABC, abstractmethod
from CNLWizard.CNLWizard import Cnl, CNAME


class Component(ABC):
    dependencies: list[Component] = []

    def __init__(self, cnl: Cnl):
        self.cnl = cnl

    @abstractmethod
    def compile(self, cnl: Cnl):
        """Add grammar rule(s) and function(s) to CNL"""


class Attribute(Component):
    def __init__(self, cnl: Cnl):
        super().__init__(cnl)

    def compile(self, cnl: Cnl) -> [str, str]:
        @cnl.rule('"with" CNAME "equal to" (CNAME | NUMBER)')
        def attribute(name, attribute_value):
            return name, attribute_value

        cnl.support_rule('attributes', 'attribute', concat=',')


class Entity(Component):
    def __init__(self, cnl: Cnl):
        super().__init__(cnl)

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
    def __init__(self, cnl: Cnl):
        super().__init__(cnl)
        self.operators = {
            'sum': '+',
            'difference': '-',
            'division': '/',
            'multiplication': '*'}

    def compile(self, cnl: Cnl):
        cnl.support_rule('math_operator', self.operators)

        @cnl.rule('"the" math_operator "between" math_operand "and" math_operand', dependencies=['math_operand'])
        def math_operation(math_operator, *args):
            if isinstance(math_operator, str):
                return math_operator.join(args)
            elif callable(math_operator):
                return math_operator(*args)

    def __setitem__(self, key, value):
        self.operators[key] = value
        self.cnl.component_changed(self)


class Comparison(Component):
    def __init__(self, cnl: Cnl):
        super().__init__(cnl)
        self.comparison_operator = {
            'sum': '+',
            'difference': '-',
            'equal to': '=',
            'different from': '!=',
            'lower than': '<',
            'greater than': '>',
            'lower than or equal to': '<=',
            'greater than or equal to': '>='
        }

    def compile(self, cnl: Cnl):
        cnl.support_rule('comparison_operator', self.comparison_operator)

        @cnl.rule('comparison_first "is"? comparison_operator comparison_second',
                  dependencies=['comparison_first', 'comparison_second'])
        def comparison(first, operator, second):
            if isinstance(operator, str):
                return f'{first}{operator}{second}'
            elif callable(operator):
                return operator(first, second)