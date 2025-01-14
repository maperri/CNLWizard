from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(*proposition):
    raise NotImplementedError


def word(l_case, string):
    return f'{l_case}{string}'


def disjunction(simple_clause, attribute):
    raise NotImplementedError


def disjunction_concat(*args): 
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def proposition(disjunction):
    raise NotImplementedError


def simple_clause(simple_proposition):
    raise NotImplementedError


def comparison_first(math):
    raise NotImplementedError


def aggregate(entity_1, verb, entity_2):
    raise NotImplementedError


def comparison_second(number):
    raise NotImplementedError


def math_first(string, entity_1, verb, entity_2):
    raise NotImplementedError


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def there_is_clause(entity):
    return Fact(entity)


def math(*args):
    operator_index = 0
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return Comparison(operator, args)


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return Comparison(operator, args)


def comparison_operator(*args):
    items_dict = {'equal to': '!=',
                  'different from': '==',
                  'less than': '>=',
                  'greater than': '<=',
                  'less than or equal to': '>',
                  'greater than or equal to': '<',
                  'at most': '<='}
    item = ' '.join(args)
    return items_dict[item]


def simple_proposition(entity_1, entity_2, entity_3):
    return entity_1, entity_2, entity_3


def negated_simple_proposition(entity_1, entity_2, entity_3):
    entity_2.negation = 'not '
    return entity_1, entity_2, entity_3


def entity(string, attribute):
    entity = Atom(CnlWizardCompiler.signatures[string.lower().removesuffix('s')])
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def verb(string_1, attribute, string_2):
    name = string_1.lower() + "_" + string_2
    entity = Signature(name, {})
    if name in CnlWizardCompiler.signatures:
        entity = Atom(CnlWizardCompiler.signatures[name])
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def weak_constraint(level, comparison):
    raise NotImplementedError


def level(*args):
    raise NotImplementedError


