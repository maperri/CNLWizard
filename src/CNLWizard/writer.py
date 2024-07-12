from __future__ import annotations

import collections
from textwrap import dedent, indent
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from CNLWizard.cnl import CompiledRule, SupportRule, AttributeRule, EntityRule, ListRule, OperationRule, \
    GrammarConfigRule, Rule, PureFunction


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
        return f'{rule.name} {concat_symbol} {rule.name} -> {rule.name}_concat\n'


class PythonFunctionWriter(RuleVisitor):
    def __init__(self, implemented_functions: set[str] = None):
        if implemented_functions is None:
            implemented_functions = set()
        self.implemented_fn = implemented_functions

    def __py_not_implemented_fn(self, name: str, args: list[str]) -> str:
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
        if not fn_args:
            fn_args.append('*args')
        return f'def {name}({", ".join(fn_args)}):\n' \
               f'   raise NotImplementedError\n\n\n'

    def visit_support_rule(self, r: SupportRule) -> str:
        py_fn = ''
        if r.name not in self.implemented_fn:
            if (not r.non_terminal_symbols and not r.name.isupper()) or len(r.get_rule_function_args()) > 1:
                # If the rule has only terminal symbols, but it is written in lower case, or
                # it has more than 1 non-terminal symbol then process it
                args = r.get_rule_function_args()
                if not args:
                    args = ['value']
                py_fn += self.__py_not_implemented_fn(r.name, args)
        if r.concat is not None and f'{r.name}_concat' not in self.implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_compiled_rule(self, r: CompiledRule) -> str:
        py_fn = ''
        if r.name not in self.implemented_fn:
            py_fn += self.__py_not_implemented_fn(r.name, r.get_rule_function_args())
        if r.concat is not None and f'{r.name}_concat' not in self.implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_attribute_rule(self, r: AttributeRule) -> str:
        py_fn = ''
        if r.name not in self.implemented_fn:
            py_fn += f'def {r.name}(name, attribute_value):\n' \
                     '    return name, attribute_value\n\n\n'
        if r.concat is not None and f'{r.name}_concat' not in self.implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_entity_rule(self, r: EntityRule) -> str:
        py_fn = ''
        if r.name not in self.implemented_fn:
            py_fn += dedent(f'''\
                    def {r.name}(name, attributes):
                        try:
                            entity = CnlWizardCompiler.signatures[name]
                            for name, value in attributes:
                                entity.fields[name] = value
                            return entity
                        except KeyError:
                            return None\n\n\n''')
        if r.concat is not None and f'{r.name}_concat' not in self.implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_list_rule(self, r: ListRule) -> str:
        py_fn = ''
        if r.name not in self.implemented_fn:
            py_fn += dedent('''\
                            def list_index_element(idx, list_name):
                                return self.cnl.lists[list_name][idx]
                    
                            def list_contains(list_name, elem):
                                return elem in self.cnl.lists[list_name]\n\n\n''')
        if r.concat is not None and f'{r.name}_concat' not in self.implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_operation_rule(self, r: OperationRule) -> str:
        py_fn = ''
        if f'{r.name}_operator' not in self.implemented_fn:
            py_fn += dedent(f'''\
                            def {r.name}_operator(*args):
                                items_dict = {str(r.operators)}
                                item = ' '.join(args)
                                return items_dict[item]
                                
                                
                            ''')
        if r.name not in self.implemented_fn:
            py_fn += dedent(f'''\
                        def {r.name}(*args):
                            operator_index = None
                            raise NotImplementedError('replace operator_index value')
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
        if r.concat is not None and f'{r.name}_concat' not in self.implemented_fn:
            py_fn += self.__concat_rule(r)
        return py_fn

    def visit_pure_function(self, r: PureFunction) -> str:
        if r.name in self.implemented_fn:
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
