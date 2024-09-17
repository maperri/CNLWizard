import copy
from abc import abstractmethod
from collections import defaultdict

from CNLWizard.writer import RuleVisitor


class Rule:
    def __init__(self, name: str, syntax: list[str], concat: str | None = None):
        if not name.isupper():
            name = name.lower()
        self.name = name
        self.syntax: list[str] = syntax
        self.non_terminal_symbols = []
        self.concat: str | None = concat

    @abstractmethod
    def accept(self, v: RuleVisitor):
        pass

    def get_non_terminal_symbols(self) -> list[str]:
        if self.non_terminal_symbols:
            # non-terminal symbols have been already computed
            # or syntax is empty
            return self.non_terminal_symbols
        curr = ''
        open_quotes = False
        for rule in self.syntax:
            for c in rule:
                if c == '"':
                    open_quotes = not open_quotes
                    curr = ''
                elif c == ' ' and not open_quotes:
                    if curr and not curr.isupper():
                        self.non_terminal_symbols.append(curr)
                    curr = ''
                else:
                    if not open_quotes and (c.isalpha() or c == '_'):
                        curr += c
            if curr:
                self.non_terminal_symbols.append(curr)
                curr = ''
        return self.non_terminal_symbols

    def get_symbols(self):
        res = []
        curr = ''
        open_quotes = False
        for rule in self.syntax:
            for c in rule:
                if c in ['(', ')', '|', '*', '+']:
                    continue
                curr += c
                if c == '"':
                    open_quotes = not open_quotes
                elif c == ' ' and not open_quotes:
                    if curr.strip():
                        res.append(curr.strip())
                    curr = ''
            if curr:
                res.append(curr)
        return res

    def get_rule_function_args(self) -> list[str]:
        curr = ''
        res = []
        open_quotes = False
        for c in self.syntax[0]:
            if c == '"':
                open_quotes = not open_quotes
                curr = ''
            elif c == ' ' and not open_quotes:
                if curr and not curr.isupper():
                    res.append(curr)
                curr = ''
            elif c == '+' or c == '*':
                # Return args with undefined length
                arg = res[0] if res else curr
                return [f'*{arg}']
            else:
                if not open_quotes and (c.isalpha() or c == '_'):
                    curr += c
        if curr and not curr.isupper():
            res.append(curr)
        return res


class GrammarConfigRule(Rule):
    def __init__(self, name: str, syntax: list[str]):
        super().__init__(name, syntax, None)
        self.name = name

    def get_non_terminal_symbols(self) -> list[str]:
        return [self.name]

    def accept(self, v: RuleVisitor):
        return v.visit_config_rule(self)


class CompiledRule(Rule):
    def __init__(self, name: str, syntax: list[str], concat: str | None = None):
        super().__init__(name, syntax, concat)

    def accept(self, v: RuleVisitor) -> str:
        return v.visit_compiled_rule(self)


class SupportRule(Rule):
    def __init__(self, name: str, syntax: list[str], concat: str | None = None):
        super().__init__(name, syntax, concat)

    def accept(self, v: RuleVisitor) -> str:
        return v.visit_support_rule(self)


class AttributeRule(Rule):
    def __init__(self, name: str, syntax: str = None, concat: str | None = None):
        if syntax is None:
            syntax = '"with" string "equal to" (string | number)'
        super().__init__(name, [syntax], concat)

    def accept(self, v: RuleVisitor):
        return v.visit_attribute_rule(self)


class EntityRule(Rule):
    def __init__(self, name: str, syntax: list[str] = None, concat: str | None = None):
        if not syntax:
            syntax = ['("A" | "An" | "a" | "an")? string attribute']
        super().__init__(name, syntax, concat)

    def accept(self, v: RuleVisitor):
        return v.visit_entity_rule(self)


class OperationRule(Rule):
    def __init__(self, name: str, operators: dict,
                 syntax: list[str] = None, concat: str | None = None):
        super().__init__(name, [f'{name}_first {name}_operator {name}_second'], concat)
        self.operators = operators
        if syntax is not None:
            self.syntax = syntax

    def accept(self, v: RuleVisitor):
        return v.visit_operation_rule(self)


class ListRule(Rule):
    def __init__(self, name: str, concat: str | None = None):
        super().__init__(name, ['"the" number "th element of" string', 'string "contains" (number | string)'], concat)

    def accept(self, v: RuleVisitor):
        return v.visit_list_rule(self)


class PureFunction(Rule):
    def __init__(self, name: str, args: list[str], body: str = None):
        super().__init__(name, args)
        if body is None:
            body = 'raise NotImplementedError'
        self.body = body

    def signature(self) -> str:
        return f'{self.name}({", ".join(self.syntax)})'

    def get_non_terminal_symbols(self) -> list[str]:
        return [self.name]

    def accept(self, v: RuleVisitor):
        return v.visit_pure_function(self)


class PreprocessConfigRule(Rule):
    def __init__(self, config_name: str):
        super().__init__(config_name, [])

    def get_non_terminal_symbols(self) -> list[str]:
        return [self.name]

    def accept(self, v: RuleVisitor):
        return v.visit_preprocess_config_rule(self)


class ImportedRule(Rule):
    def __init__(self, origin: str, rule: Rule):
        super().__init__(rule.name, rule.syntax)
        self.origin = origin
        self.rule = rule

    def get_non_terminal_symbols(self) -> list[str]:
        return [self.name]

    def accept(self, v: RuleVisitor):
        return v.import_rule(self.rule, self.origin)


class Grammar:
    def __init__(self):
        self.rules: dict[str, dict] = defaultdict(dict)  # dictionary target language - rule

    def get_rules(self, target: str) -> list[Rule]:
        visited = {}
        non_terminal_symbols: set = set()
        non_terminal_symbols.add('start')
        for rule in list(self.rules['_all'].values()) + list(self.rules[target].values()):
            non_terminal_symbols.update(rule.get_non_terminal_symbols())
        for rule in list(self.rules['_all'].values()) + list(self.rules[target].values()):
            if rule.name not in non_terminal_symbols:
                # do not include unused rules
                # they can be initialized in rules because of composite rules
                continue
            if rule.name in visited:
                # merge rules with same name
                visited[rule.name].syntax += rule.syntax
            else:
                visited[rule.name] = copy.deepcopy(rule)
        start_rule = visited['start']
        del visited['start']
        return [start_rule] + list(visited.values())

    def keys(self) -> list:
        return list(self.rules.keys())

    def items(self) -> (str, list):
        return self.rules.items()

    def values(self) -> list:
        return list(self.rules.values())

    def __getitem__(self, item):
        return self.rules[item]

    def __setitem__(self, key, value):
        self.rules[key] = value


class Cnl:
    WHITE_SPACE = 'common.WS'
    CNAME = 'common.CNAME'
    SIGNED_NUMBER = 'common.SIGNED_NUMBER'
    INT = 'common.INT'
    FLOAT = 'common.FLOAT'
    NUMBER = 'common.NUMBER'
    COMMENT = 'common.CPP_COMMENT'

    def __init__(self):
        self._grammar: Grammar = Grammar()  # dictionary target language - rule
        self.imports()

    def imports(self):
        for value in [Cnl.WHITE_SPACE, Cnl.CNAME, Cnl.SIGNED_NUMBER, Cnl.INT, Cnl.FLOAT, Cnl.NUMBER, Cnl.COMMENT]:
            rule = GrammarConfigRule(f'%import {value}', [])
            self.add_rule('_all', rule)
        self.add_rule('_all', GrammarConfigRule(f'%ignore WS', []))
        self.add_rule('_all', GrammarConfigRule(f'%ignore CPP_COMMENT', []))
        self.add_rule('_all', SupportRule('string', ['CNAME']))
        self.add_rule('_all', SupportRule('signed_number', ['SIGNED_NUMBER']))
        self.add_rule('_all', SupportRule('int', ['INT']))
        self.add_rule('_all', SupportRule('float', ['FLOAT']))
        self.add_rule('_all', SupportRule('number', ['NUMBER']))
        self.add_rule('_all', GrammarConfigRule('\n//', [' ----- Defined grammar below']))

    def add_rule(self, target: str, rule: Rule):
        self._grammar[target][rule.name] = rule

    def add_rules(self, target: str, rules: list[Rule]):
        for rule in rules:
            self.add_rule(target, rule)

    def get_grammar(self, target='_all'):
        return self._grammar[target]

    def get_languages(self) -> list[str]:
        languages = list(self._grammar.keys())
        languages.remove('_all')
        if not languages:
            # Return a generic name in case it is not defined a specific target language name
            return ['cnl']
        return languages

    def print(self, language: str, v: RuleVisitor) -> str:
        string = ''
        for rule in self._grammar.get_rules(language):
            string += rule.accept(v)
        return string
