from textwrap import dedent
import lark
from lark import Lark, UnexpectedEOF, Transformer, v_args
from CNLWizard.exception.exception import SubstitutionError

"""
Processing propositions ending with "where VAR is VALUES".
The variables are substituted into the proposition generating clones, one for each value. 
"""


class ProcessCNLTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.variable_substitution: list[dict] = []  # a list of dict with variable-value as a key-pair
                                                     # each dict of the list is a new proposition clone

    def start(self, args):
        return ''.join(args), self.variable_substitution

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
        return arg.value

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


def process_cnl_specification(cnl_specification: str):
    # grammar for identifying variable substitution proposition parts
    # that are the constructions supported by the where_token
    lark = Lark(dedent(f'''\
                %import common.WS
                %ignore WS
                %import common.NUMBER
                %import common.CNAME
                LABEL: /[A-Z]+/
                start: any+ "," where_token
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
            proposition, variables = ProcessCNLTransformer().transform(tree)
            res += substitute_variable(proposition, variables) + '\n'
        except UnexpectedEOF:
            if proposition:
                if proposition[-1].isnumeric():
                    res += proposition + ' .\n'
                else:
                    res += proposition + '.\n'
    return res
