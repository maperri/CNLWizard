import ast
import importlib.util
import os
import sys
from collections import defaultdict
from pathlib import Path
from textwrap import indent
from typing import Callable

import yaml

from CNLWizard.cnl import Cnl, SupportRule, CompiledRule, AttributeRule, EntityRule, OperationRule, ListRule, \
    PureFunction, PreprocessConfigRule, Rule, ImportedRule


class YAMLReader:
    def __init__(self, imported_libs: dict = None, lang: str = None):
        self._imported_libs = imported_libs
        self._lang = lang

    def substitute_symbols(self, rule: Rule, symbols):
        rule_symbols = rule.get_symbols()
        for i in range(len(symbols)):
            rule.syntax[0] = rule.syntax[0].replace(rule_symbols[i], symbols[i])

    def get_imported_rule(self, lib: str, target: str, rule: str) -> Rule:
        rule = rule.split('(')
        res = self._imported_libs[lib].get_grammar(target)[rule[0]]
        if len(rule) > 1:
            # new terminal symbols are defined for the rule and they are consequently replaced
            symbols = rule[1].removesuffix(')').split(',')
            self.substitute_symbols(res, symbols)
        return ImportedRule(lib, target, res)

    def read_specification(self, path: str) -> Cnl:
        cnl = Cnl()
        with open(path, 'r') as stream:
            rules = yaml.safe_load(stream)
        if not rules:
            return cnl
        for key, value in rules.items():
            for target, rules in self.read_entry(key, value).items():
                cnl.add_rules(target, rules)
        return cnl

    def read_entry(self, key, value) -> dict[str, list]:
        res = defaultdict(list)
        if key == 'config':
            res['_all'] += self.config(value)
        elif key == 'import':
            if not isinstance(value, list):
                value = [value]
            for import_query in value:
                lib_name = 'cnl_wizard'
                if 'from' in import_query:
                    lib_name = import_query['from']
                rules_to_import = import_query['rules']
                for i in range(len(import_query['source'])):
                    to_import = self.import_rules(lib_name, import_query['source'][i], rules_to_import)
                    res[import_query['target'][i]] += to_import
        elif isinstance(value, list):
            for target, rules in self.composite_rule(key.lower(), value).items():
                res[target] += rules
        else:
            if key.isupper():
                # The rule is a terminal symbol
                rule = self.support_rule(key, value)
            else:
                rule = self.compiled_rule(key, value)
            if 'target' in value:
                for target in self.target(value['target']):
                    res[target].append(rule)
            else:
                res['_all'].append(rule)
        return res

    def config(self, data: dict) -> list[PreprocessConfigRule]:
        res = []
        if 'signatures' in data and data['signatures'] == 'disabled':
            res.append(PreprocessConfigRule('signatures'))
        elif 'var_substitution' in data and data['var_substitution'] == 'disabled':
            res.append(PreprocessConfigRule('var_substitution'))
        return res

    def import_all(self, lib, target_lib):
        res = []
        for rule in self._imported_libs[lib].get_grammar(target_lib):
            res.append(self.get_imported_rule(lib, target_lib, rule))
        return res

    def import_rules(self, lib, target_lib, rules) -> [list[Rule], str]:
        if rules == '*':
            return self.import_all(lib, target_lib)
        res = []
        for rule in rules:
            res.append(self.get_imported_rule(lib, target_lib, rule))
        return res

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
        syntax = None
        if 'syntax' in data:
            syntax = data['syntax']
        return AttributeRule(name, syntax, concat)

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
                ns = {}
                fn = self._create_fn(functions[value['name']].name, value['args'],
                                     '    return None')
                exec(f'{fn}', ns)
                operators[key] = ns[functions[value['name']].name]
            else:
                # adorn string operators with quotes
                operators[key] = f'\'{value}\''
        return OperationRule(name, operators, syntax), list(functions.values())

    def _create_fn(self, name: str, args: list[str], body: str):
        declaration = f'def {name}({",".join(args)}):'
        return f'{declaration}\n{indent(body, "    ")}'

    def list_rule(self, name: str):
        return ListRule(name)

    def _substitute_question_mark(self, string: str) -> str:
        # substitute the question mark in optional tokens with
        # squared parenthesis
        res = ''
        i = len(string) - 1
        while i >= 0:
            if string[i] == '?':
                res = ']' + res
                parenthesis = 0
                quotation_mark = False
                i -= 1
                while i >= 0:
                    if string[i] == ')':
                        parenthesis += 1
                    elif string[i] == '(':
                        parenthesis -= 1
                        if not quotation_mark and not parenthesis:
                            res = f'[{string[i]}{res}'
                            break
                    elif string[i] == '"':
                        quotation_mark = not quotation_mark
                    elif string[i] == ' ' and not quotation_mark and not parenthesis:
                        res = f' [{res}'
                        break
                    res = string[i] + res
                    i -= 1
            else:
                res = string[i] + res
            i -= 1
        return res

    def syntax(self, value: str | list[str]) -> list[str]:
        res = value
        if value is None:
            return []
        if isinstance(value, dict):
            if self._lang not in value:
                raise KeyError(f"{self._lang} is not defined")
            res = [value[self._lang]]
        elif isinstance(value, str):
            res = [value]
        for idx, v in enumerate(res):
            res[idx] = self._substitute_question_mark(v).strip()
        return res

    def target(self, value: str | list[str]) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return value


class pyReader:
    def _get_functions_name_in(self, path: str) -> list[str]:
        text = Path(path).read_text()
        parsed_ast = ast.parse(text)
        functions = [n.name for n in parsed_ast.body if isinstance(n, ast.FunctionDef)]
        for line in text.splitlines():
            if line.startswith('CnlWizardCompiler.config'):
                functions.append(line)
        return functions

    def _import_module(self, path: str):
        module_name = os.path.basename(path).split('.')[0]
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

    def get_functions(self, file: str) -> dict[str, Callable]:
        if not os.path.exists(file):
            return {}
        functions = self._get_functions_name_in(file)
        self._import_module(file)
        module_name = os.path.basename(file).split('.')[0]
        module = sys.modules[module_name]
        res = {}
        for fn in functions:
            exec(f'res["{fn}"] = module.{fn}', locals())
        return res
