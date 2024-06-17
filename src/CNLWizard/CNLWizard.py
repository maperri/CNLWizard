from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

import argparse
import copy
import sys
from textwrap import indent, dedent

import lark
from lark import Lark, Transformer
from CNLWizard.ProcessCNL import process_cnl_specification

if TYPE_CHECKING:
    from CNLWizard.component import Component, Entity, MathOperation, Attribute


def cnl_type(*args):
    def wrapper(cls):
        string_format = ''
        if args:
            string_format = args[0]
        return _process_type(cls, string_format)

    return wrapper


def _create_fn(name: str, args: list[str], body: str):
    declaration = f'def {name}({",".join(args)}):'
    return f'{declaration}\n{indent(body, "    ")}'


def _process_type(cls: type, string_format: str):
    """
    Function for processing types decorated with cnl_type function.
    Setting fields with None default value and __str__ method is created from decorator argument.
    """
    if cls.__module__ in sys.modules:
        globals = sys.modules[cls.__module__].__dict__
    else:
        globals = {}
    cls_annotations = cls.__dict__.get('__annotations__', {})
    cls_init_body = ''
    for field, value in cls_annotations.items():
        cls_init_body += f'if {field} is None:\n    {field} = {value.__name__}()\nself.{field}={field}\n'
    cls_init_args = ['self'] + [f'{f} = None' for f in cls_annotations.keys()]
    cls_init_fn = _create_fn('__init__', cls_init_args, cls_init_body)
    ns = {}
    exec(cls_init_fn, globals, ns)
    setattr(cls, "__init__", ns['__init__'])
    if string_format:
        cls_str_fn = _create_fn('__str__', ['self'], f'return f\'{string_format}\'')
        exec(cls_str_fn, globals, ns)
        setattr(cls, "__str__", ns['__str__'])
    return cls


class ProductionRule:
    def __init__(self, label: str, body: list[str], prefix='', dependencies=None):
        if dependencies is None:
            dependencies: list[str] = []
        self.label = label
        self.body = body
        self.prefix = prefix
        self.dependencies = dependencies

    def __str__(self):
        join_sep = '\n' + ' ' * len(self.label) + '| '
        return f'{self.prefix}{self.label}: {join_sep.join(self.body)}'


class Grammar:
    def __init__(self):
        self._imports: list[str] = []
        self._production_rules: dict[str, ProductionRule] = {}

    def add_rule(self, label: str, body: list[str], prefix: str, dependencies: list[str]):
        self._production_rules[label] = ProductionRule(label, body, prefix, dependencies)

    def get_rule(self, label: str):
        try:
            return self._production_rules[label]
        except KeyError:
            return None

    def add_import(self, command: str, value: str):
        directive = f'%{command} {value}'
        if directive not in self._imports:
            self._imports.append(directive)

    def __str__(self):
        imports = '\n'.join(self._imports) + '\n' if self._imports else ''
        grammar = ''
        for rule in self._production_rules.values():
            has_all_dependencies_satisfied = True
            for dependence in rule.dependencies:
                """If not all the dependencies are satisfied the rule does not activate
                so that rule not defined errors are prevented. 
                Used for importing default components that may require the uer to define part(s) of them."""
                if not self.get_rule(dependence):
                    has_all_dependencies_satisfied = False
                    break
            if has_all_dependencies_satisfied:
                grammar += str(rule) + '\n'
        return imports + grammar


class Signature:
    def __init__(self, name: str, fields: dict):
        self.name = name
        self.fields = fields
        self.keys: list[str] = []
        self.type = ''

    def __str__(self):
        return f'{self.name}({",".join(map(str, self.fields.values()))})'


class Signatures:
    def __init__(self, signature_type: type = Signature, signature_field_null_value: any = '_'):
        self.signatures = dict()
        self.signature_type = signature_type
        self.signature_field_null_value = signature_field_null_value

    def __getitem__(self, item):
        return copy.deepcopy(self.signatures[item])

    def __setitem__(self, key: str, value: (str, list, list, (str, int, int))):
        """
        An item is a tuple containing the name,
        the list of fields, the list of keys (i.e. a subset of fields), and a type possibly with ranges.
        The user can set his custom signature_type and this method can
        instantiate the custom signature_type.
        Note that the user-defined signature_type must be compliant to the Signature interface.
        """
        fields_dictionary = dict()
        for field in value[1]:
            fields_dictionary.update({field: self.signature_field_null_value})
        self.signatures[key] = self.signature_type(value[0], fields_dictionary)
        self.signatures[key].keys = value[2]
        self.signatures[key].type = value[3][0] if value[3] else None
        if value[3]:
            if value[3][1]:
                self.signatures[key].lb = int(value[3][1])
            else:
                self.signatures[key].lb = None
            if value[3][2]:
                self.signatures[key].ub = int(value[3][2])
            else:
                self.signatures[key].ub = None


class CNLTransformer(Transformer):
    """
    Compiling the CNL specification.
    The default function call the corresponding defined function.
    """

    def __init__(self, functions: dict):
        super().__init__()
        self._functions = functions

    def __default__(self, data, children, meta):
        if data in self._functions:
            if not children:
                return lark.Discard
            call_res = self._functions[data](*children)
            if call_res is None:
                return lark.Discard
            return call_res
        return children

    def __default_token__(self, token):
        return token.value


WHITE_SPACE = 'common.WS'
CNAME = 'common.CNAME'
WORD = 'common.WORD'
SIGNED_NUMBER = 'common.SIGNED_NUMBER'
INT = 'common.INT'
FLOAT = 'common.FLOAT'
NUMBER = 'common.NUMBER'
COMMENT = 'common.CPP_COMMENT'


class Cnl:
    CNL_START = 'cnl_start'
    signatures = Signatures()

    def __init__(self, start_token: str = 'start', signatures: Signatures = Signatures()):
        self._grammar = Grammar()
        self._start_token = start_token
        self._functions: dict = dict()
        Cnl.signatures = signatures
        self.vars = dict()
        from CNLWizard.component import Attribute, Entity, MathOperation, Comparison
        self.attribute = Attribute(self)
        self.entity = Entity(self)
        self.math_operation = MathOperation(self)
        self.comparison = Comparison(self)
        self.components = [self.attribute, self.entity, self.math_operation, self.comparison]
        self._init_defaults()

    def _init_signature_definitions(self):
        self.import_token(CNAME)
        self.import_token(NUMBER)
        self.support_rule("signature_parameters", '("a" | "an")? CNAME', concat=',')

        @self.rule('"is" ("a"|"an")? CNAME "concept" ["that ranges from" NUMBER "to" NUMBER] ", and it"')
        def typed_signature(name, lb, ub):
            return name, lb, ub

        @self.rule('("A" | "An")? CNAME [typed_signature] "is identified by" signature_parameters '
                   '["and has" signature_parameters] "."')
        def signature_definition(name, type, keys, parameters):
            fields = keys.copy()
            if parameters:
                fields += parameters
            self.signatures[name] = name, fields, keys, type

    def _init_defaults(self):
        """
        Add the signature definitions to the user-defined CNL.
        """
        self.ignore_token(WHITE_SPACE)
        # Signature definition
        self._init_signature_definitions()
        self.support_rule(Cnl.CNL_START,
                          f'signature_definition* {self._start_token}')
        ns = {}
        exec(_create_fn(self._start_token, ['*args'], 'res = ""\n'
                                                      'for arg in args:\n'
                                                      '    if arg:\n'
                                                      '        res += str(arg) + \"\\n\"\n'
                                                      'return res'), ns)
        exec(_create_fn(Cnl.CNL_START, ['*args'], 'return args[-1]'), ns)
        self._add_function(self._start_token, ns[self._start_token])
        # Start
        self._add_function(Cnl.CNL_START, ns[Cnl.CNL_START])
        for component in self.components:
            self._import_component(component)

    def _import_component(self, component: Component):
        for dependence in component.dependencies:
            self._import_component(dependence)
        component.compile(self)

    def rule(self, string: str, /, *args, concat=None, dependencies=None):
        if dependencies is None:
            dependencies = []

        def wrapper(function):
            self._add_rule(function.__name__, [string] + list(args), concat, dependencies=dependencies)
            self._add_function(function.__name__, function)
            return function

        return wrapper

    def extends(self, string: str, /, *args, concat=None):
        def wrapper(function):
            label = function.__name__
            starting_rule = self._grammar.get_rule(label)
            self._grammar.add_rule(f'primitive_{starting_rule.label}', starting_rule.body, prefix=starting_rule.prefix,
                                   dependencies=starting_rule.dependencies)
            self._functions[f'primitive_{starting_rule.label}'] = self._functions[starting_rule.label]
            rule_body = string.replace(starting_rule.label, f'primitive_{starting_rule.label}')
            self._add_rule(function.__name__, [rule_body] + list(args), concat)
            self._add_function(function.__name__, function)
            return function

        return wrapper

    def component_changed(self, component: Component):
        self._import_component(component)

    def ignore_token(self, token: str):
        self._grammar.add_import('import', token)
        self._grammar.add_import('ignore', token.split('.')[-1])

    def import_token(self, token: str):
        self._grammar.add_import('import', token)

    def _add_function(self, function_name, function):
        self._functions.update({function_name: function})

    def support_rule(self, label: str, body: str | dict, /, *args, concat=None, dependencies=None):
        prefix = ''
        if dependencies is None:
            dependencies: list[str] = []
        if isinstance(body, str):
            if concat is None and not label.isupper():
                prefix = '?'
            self._add_rule(label, [body] + list(args), concat, prefix, dependencies)
        elif isinstance(body, dict):
            prefix = '!'
            self._add_rule(label, list([f'"{key}"' for key in body.keys()]), concat, prefix, dependencies)
            ns = {}
            exec(_create_fn(label, ['item'], dedent(f'''\
                                                         items = body
                                                         return items[item]
                                                         ''')), locals(), ns)
            self._add_function(label, ns[label])
        else:
            raise RuntimeError()

    def _add_rule(self, label: str, body: list[str], concat: str | None, prefix='', dependencies=None):
        if dependencies is None:
            dependencies: list[str] = []
        if concat is not None:
            ns = {}
            if label not in self._functions:
                exec(_create_fn(label, ['elem'], 'return [elem]'), ns)
                self._add_function(label, ns[label])
            concat = f' \"{concat}\" ' if concat else ' '  # it is possible to have empty concat: rule: body | rule rule
            body += [f'{label}{concat}{label} -> {label}_concatenation']
            concatenation_fn_body = dedent('''\
                                            if elem1 is None:
                                                return elem2
                                            if elem2 is None:
                                                return elem1
                                            return elem1 + elem2''')
            exec(_create_fn(f'{label}_concatenation', ['elem1=None', 'elem2=None'], concatenation_fn_body), ns)
            self._add_function(f'{label}_concatenation', ns[f'{label}_concatenation'])
        self._grammar.add_rule(label, body, prefix, dependencies)

    def compile(self, input_txt: str = None):
        if input_txt is None:
            parser = argparse.ArgumentParser()
            parser.add_argument('input_file', nargs='?')
            args = parser.parse_args()
            input_txt = open(args.input_file, 'r').read()
        lark = Lark(str(self._grammar), start=Cnl.CNL_START)
        processed_cnl = process_cnl_specification(input_txt)
        parse_tree = lark.parse(processed_cnl)
        return CNLTransformer(self._functions).transform(parse_tree)
