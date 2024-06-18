from __future__ import annotations

from abc import ABC, abstractmethod
from CNLWizard.CNLWizard import Cnl, CNAME


class Component(ABC):
    dependencies: list[Component] = []

    def __init__(self, cnl: Cnl):
        self.cnl = cnl

    @abstractmethod
    def compile(self):
        """Add grammar rule(s) and function(s) to CNL"""


class Attribute(Component):
    def __init__(self, cnl: Cnl):
        super().__init__(cnl)

    def compile(self) -> [str, str]:
        @self.cnl.rule('"with" CNAME "equal to" (CNAME | NUMBER)')
        def attribute(name, attribute_value):
            return name, attribute_value

        self.cnl.support_rule('attributes', 'attribute', concat=',')


class Entity(Component):
    def __init__(self, cnl: Cnl):
        super().__init__(cnl)

    def compile(self) -> [str, str]:
        @self.cnl.rule('("a" | "an")? CNAME attributes', dependencies=['attributes'])
        def entity(name, attributes):
            try:
                entity = Cnl.signatures[name]
                for name, value in attributes:
                    entity.fields[name] = value
                return entity
            except KeyError:
                return None


class MathOperation(Component):
    def __init__(self, cnl: Cnl, compute=False):
        super().__init__(cnl)
        self.compute = compute
        self.operators = {
            'sum': '+',
            'difference': '-',
            'division': '/',
            'multiplication': '*'}

    def compile(self):
        self.cnl.support_rule('math_operator', self.operators)

        @self.cnl.rule('"the" math_operator "between" math_operand "and" math_operand', dependencies=['math_operand'])
        def math_operation(math_operator, *args):
            if isinstance(math_operator, str):
                if self.compute:
                    ns = {}
                    exec('res=' + math_operator.join([f'args[{i}]' for i in range(len(args))]), locals(), ns)
                    return ns['res']
                return math_operator.join(args)
            elif callable(math_operator):
                return math_operator(*args)

    def __setitem__(self, key, value):
        self.operators[key] = value
        self.cnl.component_changed(self)


class Comparison(Component):
    def __init__(self, cnl: Cnl, compute=False):
        super().__init__(cnl)
        self.compute = False
        self.comparison_operator = {
            'sum': '+',
            'difference': '-',
            'equal to': '==',
            'different from': '!=',
            'lower than': '<',
            'greater than': '>',
            'lower than or equal to': '<=',
            'greater than or equal to': '>='
        }

    def compile(self):
        self.cnl.support_rule('comparison_operator', self.comparison_operator)

        @self.cnl.rule('comparison_first "is"? comparison_operator comparison_second',
                       dependencies=['comparison_first', 'comparison_second'])
        def comparison(first, operator, second):
            if isinstance(operator, str):
                if self.compute:
                    ns = {}
                    exec(f'res=first{operator}second', locals(), ns)
                    return ns['res']
                return f'{first}{operator}{second}'
            elif callable(operator):
                return operator(first, second)

    def __setitem__(self, key, value):
        self.comparison_operator[key] = value
        self.cnl.component_changed(self)


class Formula(Component):
    def __init__(self, cnl: Cnl):
        super().__init__(cnl)
        self.formula_operator = {
            'and': '&',
            'or': '|',
            'imply': '->',
            'implies': '->',
            'is equivalent to': '<->',
            'not': '!'
        }

    def compile(self):
        self.cnl.support_rule('formula_operator', self.formula_operator)

        @self.cnl.rule('formula_first formula_operator formula_second',
                       dependencies=['formula_first', 'formula_second'])
        def formula(first, operator, second):
            if isinstance(operator, str):
                return f'{first}{operator}{second}'
            elif callable(operator):
                return operator(first, second)

    def __setitem__(self, key, value):
        self.formula_operator[key] = value
        self.cnl.component_changed(self)


class CnlList(Component):
    def __init__(self, cnl: Cnl):
        super().__init__(cnl)

    def compile(self):
        pass

