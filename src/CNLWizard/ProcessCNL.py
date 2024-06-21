from __future__ import annotations
from textwrap import dedent
from typing import TYPE_CHECKING

import lark
from lark import Lark, UnexpectedEOF, Transformer, v_args
from CNLWizard.exception.exception import SubstitutionError

if TYPE_CHECKING:
    from CNLWizard.CNLWizard import CnlWizard

"""
Processing propositions ending with "where VAR is VALUES".
The variables are substituted into the proposition generating clones, one for each value. 
"""


class ProcessCNLTransformer(Transformer):
    def __init__(self, cnl: CnlWizard):
        super().__init__()
        self.cnl = cnl
        self.variable_substitution: list[dict] = []  # a list of dict with variable-value as a key-pair
                                                     # each dict of the list is a new proposition clone

    def start(self, args):
        return ''.join(args[-1])

    def proposition(self, args):
        return args

    @v_args(inline=True)
    def signature_definition(self, name, type, keys, parameters):
        fields = keys.copy()
        if parameters:
            fields += parameters
        self.cnl.signatures[name] = name, fields, keys, type
        return ''

    @v_args(inline=True)
    def typed_signature(self, name, lb, ub):
        return name, lb, ub

    def signature_parameters(self, name):
        return name

    @v_args(inline=True)
    def signature_parameters_concat(self, first, second):
        return first + second

    @v_args(inline=True)
    def cnl_list_definition(self, name, values):
        self.cnl.lists[name] = {}
        for i in range(len(values)):
            self.cnl.lists[name][i] = values[i]
        return ''

    def cnl_list_elem(self, arg):
        return arg

    @v_args(inline=True)
    def cnl_list_elem_concat(self, first, second):
        return first + second

    def any(self, args):
        return args[0].value if args[0].value else ' '

    def where_token(self, args):
        return lark.Discard

    @v_args(meta=True)
    def where_token_between(self, meta, args):
        values = list(range(int(args[2]), int(args[3]) + 1))
        self.where_token_one_of(meta, [args[0], args[1]] + values)
        return lark.Discard

    @v_args(meta=True)
    def where_token_one_of(self, meta, args):
        values = args[2:]
        if len(values) == 1 and values[0] in self.cnl.lists:
            values = self.cnl.lists[values[0]].values()
        if not self.variable_substitution:
            for value in values:
                self.variable_substitution.append({args[0]: value})
        else:
            if not args[1]:  # args[1] == "respectively"
                new_array = []
                for variable in self.variable_substitution:
                    for value in values:
                        curr = variable.copy()
                        curr[args[0]] = value
                        new_array.append(curr)
                self.variable_substitution = new_array
            else:
                if len(values) != len(self.variable_substitution):
                    raise SubstitutionError(
                        f"Lists do not match for variable substitution in proposition {meta.line + 1}")
                for i in range(len(values)):
                    self.variable_substitution[i][args[0]] = values[i]
        return lark.Discard

    def where_distinct(self, args):
        for variable in self.variable_substitution:
            curr_value = variable[args[0]]
            for distinct_var in args[1:]:
                if variable[distinct_var] == curr_value:
                    self.variable_substitution.remove(variable)
        return lark.Discard

    def respectively(self, args):
        return True

    def CNAME(self, arg):
        return arg.value

    def NUMBER(self, arg):
        return int(arg.value)

    def LABEL(self, arg):
        return arg.value


def substitute_variable(proposition, variables):
    res = []
    if not variables:
        return proposition
    for variable in variables:
        curr = proposition
        for key, value in variable.items():
            curr = curr.replace(key, str(value))
        if curr[-1].isnumeric():
            curr += ' '
        res.append(f'{curr}.')
    return '\n'.join(res)


def process_cnl_specification(cnl: CnlWizard, cnl_specification: str):
    # grammar for identifying variable substitution proposition parts
    # that are the constructions supported by the where_token
    lark = Lark(dedent(f'''\
                %import common.WS
                %ignore WS
                %import common.NUMBER
                %import common.CNAME
                LABEL: /[A-Z]+/
                start: definition | proposition
                signature_definition: ("A" | "An")? CNAME [typed_signature] "is identified by" signature_parameters ["and has" signature_parameters]
                typed_signature: "is" ("a"|"an")? CNAME "concept" ["that ranges from" NUMBER "to" NUMBER] ", and it"
                cnl_list_elem: NUMBER | CNAME
                             | cnl_list_elem "," cnl_list_elem -> cnl_list_elem_concat
                signature_parameters: ("a" | "an")? CNAME 
                                    | signature_parameters "," signature_parameters -> signature_parameters_concat
                cnl_list_definition: ("A" | "An") CNAME "is a list made of" cnl_list_elem
                ?definition.1: signature_definition | cnl_list_definition
                proposition: any+ "," where_token
                any: /.+?/ 
                ?where_token.1: where_token_between | where_token_one_of | where_distinct | where_token "," where_token
                where_token_between: "where" LABEL "is" [respectively] "between" NUMBER "and" NUMBER 
                where_token_one_of: "where" LABEL "is" [respectively] "one" "of" (CNAME | NUMBER) (","? "and"? (CNAME | NUMBER))*
                where_distinct: "where" LABEL (","? "and"? LABEL) "are distinct"
                respectively: "respectively"
                '''), propagate_positions=True)
    res = ''
    for idx, proposition in enumerate(cnl_specification.split('.')):
        try:
            proposition = proposition.strip()
            tree = lark.parse(proposition)
            transf = ProcessCNLTransformer(cnl)
            proposition = transf.transform(tree)
            if proposition:
                if transf.variable_substitution:
                    res += substitute_variable(proposition, transf.variable_substitution) + '\n'
        except UnexpectedEOF:
            if proposition:
                if proposition[-1].isnumeric():
                    res += proposition + ' .\n'
                else:
                    res += proposition + '.\n'
    return res
