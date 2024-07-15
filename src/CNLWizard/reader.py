import ast
import importlib.util
import os
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from CNLWizard.cnl import Cnl, SupportRule, CompiledRule, AttributeRule, EntityRule, OperationRule, ListRule, \
    PureFunction


class YAMLReader:
    def read_specification(self, path: str) -> Cnl:
        cnl = Cnl()
        with open(path, 'r') as stream:
            rules = yaml.safe_load(stream)
        for key, value in rules.items():
            if isinstance(value, list):
                for target, rules in self.composite_rule(key.lower(), value).items():
                    cnl.add_rules(target, rules)
            else:
                if key.isupper():
                    # The rule is a terminal symbol
                    rule = self.support_rule(key, value)
                else:
                    rule = self.compiled_rule(key, value)
                if 'target' in value:
                    for target in self.target(value['target']):
                        cnl.add_rule(target, rule)
                else:
                    cnl.add_rule('_all', rule)
        return cnl

    def support_rule(self, name: str, data: dict) -> SupportRule:
        concat = None
        if 'concat' in data:
            concat = data['concat']
        return SupportRule(name, self.syntax(data['syntax']), concat)

    def compiled_rule(self, name: str, data: dict) -> CompiledRule:
        concat = None
        if 'concat' in data:
            concat = data['concat']
        return CompiledRule(name, self.syntax(data['syntax']), concat)

    def composite_rule(self, name: str, rules: list) -> dict[str, list]:
        composite: dict[str, list] = defaultdict(list)  # dict of target and corresponding instances name
        instances: dict[str, list] = defaultdict(list)  # dict of target and corresponding rules
        for rule in rules:
            rule_targets = self.target(rule['target']) if 'target' in rule else self.target('_all')
            syntax = []
            if 'syntax' in rule:
                syntax = self.syntax(rule['syntax'])
            concat = None
            if 'concat' in rule:
                concat = rule['concat']
            for target in rule_targets:
                if name == 'operation':
                    instance, functions = self.operation_rule(rule['name'], rule)
                    instances[target] += functions
                elif name == 'attribute':
                    instance = self.attribute_rule(rule['name'], rule)
                elif name == 'entity':
                    instance = self.entity_rule(rule['name'], rule)
                elif name == 'list':
                    instance = self.list_rule(rule['name'])
                else:
                    if syntax:
                        instance = CompiledRule(rule['name'], syntax, concat)
                    else:
                        # In this case, the user should have defined the rule somewhere else
                        instance = None
                if instance:
                    instances[target].append(instance)
                composite[target].append(rule['name'])
        for key, value in composite.items():
            if name not in composite[key]:
                # do not create a composite rule, if an instance
                # has the same name of the composite rule itself
                instances[key].append(CompiledRule(name, value, None))
        return instances

    def attribute_rule(self, name: str, data: dict) -> AttributeRule:
        concat = None
        if 'concat' in data:
            concat = data['concat']
        return AttributeRule(name, concat)

    def entity_rule(self, name: str, data: dict) -> EntityRule:
        concat = None
        if 'concat' in data:
            concat = data['concat']
        syntax = []
        if 'syntax' in data:
            syntax = self.syntax(data['syntax'])
        return EntityRule(name, syntax, concat)

    def operation_rule(self, name: str, data: dict) -> [OperationRule, list[PureFunction]]:
        syntax = None
        operators = {}
        functions = {}
        if 'syntax' in data:
            syntax = self.syntax(data['syntax'])
        if 'operators' in data:
            operators = data['operators']
        # process functions inside operators
        for key, value in operators.items():
            if isinstance(value, dict):
                value = value['fun']
                fn = PureFunction(value['name'], value['args'])
                functions[value['name']] = fn
                operators[key] = functions[value['name']].name
            else:
                # adorn string operators with quotes
                operators[key] = f'\'{value}\''
        return OperationRule(name, operators, syntax), list(functions.values())

    def list_rule(self, name: str):
        return ListRule(name)

    def syntax(self, value: str | list[str]) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()]
        return [v.strip() for v in value]

    def target(self, value: str | list[str]) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return value


class pyReader:
    def read_module(self, path: str) -> list[str]:
        parsed_ast = ast.parse(Path(path).read_text())
        functions = [
            node.name
            for node in ast.walk(parsed_ast)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        return functions

    def import_module(self, path: str):
        module_name = os.path.basename(path).split('.')[0]
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
