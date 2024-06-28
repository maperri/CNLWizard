from __future__ import annotations

from abc import ABC, abstractmethod
from CNLWizard.CNLWizard import CnlWizard


class Component(ABC):
    def __init__(self, cnl: CnlWizard, name: str):
        self.cnl = cnl
        self.name = name

    @abstractmethod
    def compile(self):
        """Add grammar rule(s) and function(s) to CNL"""


class Attribute(Component):
    def __init__(self, cnl: CnlWizard, name: str):
        super().__init__(cnl, name)

    def compile(self) -> [str, str]:
        @self.cnl.rule('"with" CNAME "equal to" (CNAME | NUMBER)')
        def attribute(name, attribute_value):
            return name, attribute_value

        self.cnl.support_rule('attributes', 'attribute', concat=',')


class Entity(Component):
    def __init__(self, cnl: CnlWizard, name: str):
        super().__init__(cnl, name)

    def compile(self) -> [str, str]:
        @self.cnl.rule('("a" | "an")? CNAME attributes', dependencies=['attributes'])
        def entity(name, attributes):
            try:
                entity = CnlWizard.signatures[name]
                for name, value in attributes:
                    entity.fields[name] = value
                return entity
            except KeyError:
                return None


class Operation(Component):
    def __init__(self, cnl: CnlWizard, name: str, operators: dict,
                 rule_body: list[str, str] = None, rule_dependencies: list[str] = None, compute=False):
        """
        param rule_body: contains a list of two elements.
            The first element contains the grammar rule,
            the second element contains the operators and operands order.

            The order is expressed by a string containing
            a space separated 'operand' and 'operator' string.

            Operator must be labeled in the rule as {operation_name}_operator.
        """
        super().__init__(cnl, name)
        self.compute = compute
        self.operators = operators
        if rule_body is None:
            self.rule_body = f'{self.name}_first {self.name}_operator {self.name}_second'
            self.rule_dependencies = [f'{self.name}_first', f'{self.name}_first']
        else:
            self.rule_body = rule_body[0]
            self.parameters_order = rule_body[1].split()
        if rule_dependencies is not None:
            self.rule_dependencies = rule_dependencies

    def compile(self):
        self.cnl.support_rule(f'{self.name}_operator', self.operators)

        @self.cnl.rule(f'{self.rule_body}',
                       dependencies=self.rule_dependencies, name=self.name)
        def operation_component(*args):
            operator_index = self.parameters_order.index('operator')
            operator = args[operator_index]
            args = list(args)
            args.pop(operator_index)
            if isinstance(operator, str):
                if self.compute:
                    ns = {}
                    exec('res=' + operator.join([f'args[{i}]' for i in range(len(args))]), locals(), ns)
                    return ns['res']
                return operator.join(map(str, args))
            elif callable(operator):
                return operator(*args)

    def __setitem__(self, key, value):
        self.operators[key] = value
        self.compile()


class CnlList(Component):
    def __init__(self, cnl: CnlWizard, name: str):
        super().__init__(cnl, name)

    def compile(self):
        @self.cnl.rule('"the" NUMBER "th element of" CNAME')
        def list_index_element(idx, list_name):
            return self.cnl.lists[list_name][idx]

        @self.cnl.rule('CNAME "contains" (NUMBER | CNAME)')
        def list_contains(list_name, elem):
            return elem in self.cnl.lists[list_name]


class UnitProposition(Component):

    def __init__(self, cnl: CnlWizard, name: str,
                 rule_body: str, rule_dependencies: list[str]):
        super().__init__(cnl, name)
        self.rule_body = rule_body
        self.rule_dependencies = rule_dependencies

    def compile(self):
        self.cnl.support_rule(self.name, self.rule_body, dependencies=self.rule_dependencies)
