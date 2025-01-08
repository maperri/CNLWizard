from __future__ import annotations

import collections
import inspect
from inspect import signature
from textwrap import dedent, indent
from typing import TYPE_CHECKING
import types

if TYPE_CHECKING:
    from CNLWizard.cnl import CompiledRule, SupportRule, AttributeRule, EntityRule, ListRule, OperationRule, \
        GrammarConfigRule, Rule, PureFunction, PreprocessConfigRule, Cnl


class RuleVisitor:
    def visit_compiled_rule(self, r: CompiledRule) -> str:
        return ''

    def visit_support_rule(self, r: SupportRule) -> str:
        return ''

    def visit_attribute_rule(self, r: AttributeRule) -> str:
        return ''

    def visit_entity_rule(self, r: EntityRule) -> str:
        return ''

    def visit_list_rule(self, r: ListRule) -> str:
        return ''

    def visit_operation_rule(self, r: OperationRule) -> str:
        return ''

    def visit_config_rule(self, r: GrammarConfigRule) -> str:
        return ''

    def visit_pure_function(self, r: PureFunction) -> str:
        return ''

    def visit_preprocess_config_rule(self, r: PreprocessConfigRule) -> str:
        return ''

    def import_rule(self, r: Rule, origin: str, target: str) -> str:
        return ''


class LarkGrammarWriter(RuleVisitor):
    def visit_compiled_rule(self, r: CompiledRule) -> str:
        name = f'{r.name}'
        if not r.get_non_terminal_symbols():
            name = f'!{name}'
        rule = f'{name}: {" | ".join(r.syntax)}\n'
        if r.concat is not None:
            rule += f'{" " * len(r.name)}| {self.__concat_rule(r)}'
        return rule

    def visit_support_rule(self, r: SupportRule) -> str:
        prefix = ''
        if not r.name.isupper():
            prefix = '?'
        if not r.non_terminal_symbols and not r.name.isupper():
            prefix = '!'
        rule = f'{prefix}{r.name}: {" | ".join(r.syntax)}\n'
        if r.concat is not None:
            rule += f'{" " * len(r.name)}| {self.__concat_rule(r)}'
        return rule

    def visit_attribute_rule(self, r: AttributeRule) -> str:
        rule = f'{r.name}: {" | ".join(r.syntax)}\n'
        if r.concat is not None:
            rule += f'{" " * len(r.name)}| {self.__concat_rule(r)}'
        return rule

    def visit_entity_rule(self, r: EntityRule) -> str:
        rule = f'{r.name}: {" | ".join(r.syntax)}\n'
        if r.concat is not None:
            rule += f'{" " * len(r.name)}| {self.__concat_rule(r)}'
        return rule

    def visit_list_rule(self, r: ListRule) -> str:
        rule = f'{r.name}: {r.syntax[0]} -> list_index_element\n' \
               f'{" " * len(r.name)}| {r.syntax[1]} -> list_contains\n'
        if r.concat is not None:
            rule += f'{" " * len(r.name)}| {self.__concat_rule(r)}'
        return rule

    def visit_operation_rule(self, r: OperationRule) -> str:
        rule = ''
        operators = [f'"{op}"' for op in r.operators.keys()]
        rule += f'!{r.name}_operator: {" | ".join(operators)}\n'
        rule += f'{r.name}: {" | ".join(r.syntax)}\n'
        if r.concat is not None:
            rule += f'{" " * len(r.name)}| {self.__concat_rule(r)}'
        return rule

    def visit_config_rule(self, r: GrammarConfigRule):
        syntax = ''
        if r.syntax:
            syntax = ''.join(r.syntax)
        return f'{r.name} {syntax}\n'

    def __concat_rule(self, rule: Rule):
        concat_symbol = f'"{rule.concat}"'
        if not rule.concat.strip():
            concat_symbol = ''
        return f'{rule.name} {concat_symbol} {rule.name} -> {rule.name}_concat\n'

    def import_rule(self, r: Rule, origin: str, target: str) -> str:
        return r.accept(self)


class PythonFunctionWriter(RuleVisitor):
    def __init__(self, imported_fn: dict = None):
        self._implemented_fn = set()
        self._import_libs = ['from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler']
        self._imported_fn = imported_fn

    def __create_unique_args(self, args: list[str]) -> list[str]:
        args_counter = collections.Counter(args)
        fn_args = []
        for arg in args[::-1]:
            if args_counter[arg] > 1:
                # add an index to duplicated args names
                fn_args.insert(0, f'{arg}_{args_counter[arg]}')
                args_counter[arg] -= 1
            else:
                if f'{arg}_{2}' in fn_args:
                    fn_args.insert(0, f'{arg}_{args_counter[arg]}')
                else:
                    fn_args.insert(0, arg)
        return fn_args

    def __py_not_implemented_fn(self, name: str, args: list[str]) -> str:
        fn_args = self.__create_unique_args(args)
        if not fn_args:
            fn_args.append('*args')
        return f'def {name}({", ".join(fn_args)}):\n' \
               f'    raise NotImplementedError\n\n\n'

    def visit_support_rule(self, r: SupportRule) -> str:
        py_fn = ''
        if r.name not in self._implemented_fn:
            if (not r.non_terminal_symbols and not r.name.isupper()) or len(r.get_rule_function_args()) > 1:
                # If the rule has only terminal symbols, but it is written in lower case, or
                # it has more than 1 non-terminal symbol then process it
                args = r.get_rule_function_args()
                if not args:
                    args = ['value']
                py_fn += self.__py_not_implemented_fn(r.name, args)
        if r.concat is not None and f'{r.name}_concat' not in self._implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_compiled_rule(self, r: CompiledRule) -> str:
        py_fn = ''
        if r.name not in self._implemented_fn:
            if not r.code:
                py_fn += self.__py_not_implemented_fn(r.name, r.get_rule_function_args())
            else:
                py_fn += dedent(f'''\
                                def {r.name}({", ".join(r.get_rule_function_args())}):
                                {indent(r.code, '    ')}\n\n\n''')
        if r.concat is not None and f'{r.name}_concat' not in self._implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_attribute_rule(self, r: AttributeRule) -> str:
        py_fn = ''
        if r.name not in self._implemented_fn:
            py_fn += f'def {r.name}(name, attribute_value):\n' \
                     '    return [(name, attribute_value)]\n\n\n'
        if r.concat is not None and f'{r.name}_concat' not in self._implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_entity_rule(self, r: EntityRule) -> str:
        py_fn = ''
        if r.name not in self._implemented_fn:
            py_fn += dedent(f'''\
                    def {r.name}({', '.join(self.__create_unique_args(r.get_rule_function_args()))}):
                        try:
                            entity = CnlWizardCompiler.signatures[string]
                            for name, value in attribute:
                                entity.fields[name] = value
                            return entity
                        except KeyError:
                            return None\n\n\n''')
        if r.concat is not None and f'{r.name}_concat' not in self._implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_list_rule(self, r: ListRule) -> str:
        py_fn = ''
        if r.name not in self._implemented_fn:
            py_fn += dedent('''\
                            def list_index_element(idx, list_name):
                                return self.cnl.lists[list_name][idx]
                    
                            def list_contains(list_name, elem):
                                return elem in self.cnl.lists[list_name]\n\n\n''')
        if r.concat is not None and f'{r.name}_concat' not in self._implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def __dict_to_str(self, d: dict) -> str:
        res = '{'
        for key, value in d.items():
            if isinstance(value,  types.FunctionType):
                value = f'{value.__name__}{signature(value)}'
            res += f'\'{key}\': {value}, '
        return res.removesuffix(', ') + '}'

    def visit_operation_rule(self, r: OperationRule) -> str:
        py_fn = ''
        if f'{r.name}_operator' not in self._implemented_fn:
            py_fn += dedent(f'''\
                            def {r.name}_operator(*args):
                                items_dict = {self.__dict_to_str(r.operators)}
                                item = ' '.join(args)
                                return items_dict[item]
                                
                                
                            ''')
        if r.name not in self._implemented_fn:
            operator_index = 0
            for o in r.get_rule_function_args():
                if o.endswith('operator'):
                    break
                operator_index += 1
            py_fn += dedent(f'''\
                        def {r.name}(*args):
                            operator_index = {operator_index}
                            operator = args[operator_index]
                            args = list(args)
                            args.pop(operator_index)
                            ''')
            if isinstance(list(r.operators.values())[0], str):
                py_fn += f'    return operator.join(map(str, args))\n\n\n'
            elif callable(list(r.operators.values())[0]):
                py_fn += '    return operator(*args)\n\n\n'
            else:
                py_fn += '\n\n\n'
        if r.concat is not None and f'{r.name}_concat' not in self._implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_pure_function(self, r: PureFunction) -> str:
        if r.name in self._implemented_fn:
            return ''
        return dedent(f'''\
                def {r.name}({", ".join(r.syntax)}):
                {indent(r.body, '    ')}\n\n\n''')

    def __concat_rule(self, rule: Rule):
        fn_name = f'{rule.name}_concat'
        return dedent(f'''\
                    def {fn_name}(*args): 
                        res = []
                        for arg in args:
                            if not isinstance(arg, list):
                                arg = [arg]
                            res += arg
                        return res\n\n\n''')

    def visit_preprocess_config_rule(self, r: GrammarConfigRule) -> str:
        res = f'CnlWizardCompiler.config[\'{r.name}\'] = False'
        if res not in self._implemented_fn:
            return f'{res}\n\n\n'
        return ''

    def import_fn(self, py_file):
        from CNLWizard.reader import pyReader
        self._implemented_fn = set(pyReader().get_functions(py_file).keys())

    def write(self, content: str, py_file: str):
        if self._implemented_fn:
            with open(py_file, 'a') as out:
                out.write(f'{content}')
        else:
            with open(py_file, 'w') as out:
                libs = '\n'.join(self._import_libs)
                out.write(f'{libs}\n\n\n{content}')

    def import_rule(self, r: Rule, origin: str, target: str) -> str:
        if r.name in self._implemented_fn:
            return ''
        if r.name in self._imported_fn[origin][target]:
            res = ''
            for name in r.get_to_import():
                res += inspect.getsource(self._imported_fn[origin][target][name]) + '\n\n'
            return res
        return r.accept(self)
