from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


import copy

from CNLWizard.libs.asp import *


def start(*proposition):
    res = ''
    for p in proposition:
        if isinstance(p, list):
            p = '\n'.join(map(str, p))
        res += str(p) + '\n'
    return res


def start_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def attribute_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def proposition(disjunction):
    return disjunction


def simple_clause(simple_proposition):
    field = simple_proposition[0].name + '_' + str(list(simple_proposition[0].fields.keys())[0])
    simple_proposition[1].fields[field] = list(simple_proposition[0].fields.values())[0]
    field = simple_proposition[2].name + '_' + str(list(simple_proposition[2].fields.keys())[0])
    simple_proposition[1].fields[field] = list(simple_proposition[2].fields.values())[0]
    return simple_proposition[1], simple_proposition[2]


def disjunction(simple_1, attribute):
    simple_2 = copy.deepcopy(simple_1[0])
    simple_2.fields[simple_1[1].name + '_' + attribute[0][0]] = attribute[0][1]
    return Assignment([simple_1[0], simple_2], [])


def math_first(string, entity_1, verb, entity_2):
    entity_1.fields[string] = 'COUNT_VAR'
    entity_1.fields[list(entity_1.fields.keys())[0]] = 'X'
    field = entity_1.name + '_' + str(list(entity_1.fields.keys())[0])
    verb.fields[field] = list(entity_1.fields.values())[0]
    field = entity_2.name + '_' + str(list(entity_2.fields.keys())[0])
    verb.fields[field] = list(entity_2.fields.values())[0]
    return 'COUNT_VAR', entity_1, verb


def comparison_first(math):
    return math


def comparison_second(number):
    return number


def aggregate(entity_1, verb, entity_2):
    field = list(entity_1.fields.keys())[0]
    verb.fields[entity_1.name + '_' + field] = 'C'
    field = list(entity_2.fields.keys())[0]
    verb.fields[entity_2.name + '_' + field] = entity_2.fields[list(entity_2.fields.keys())[0]]
    return Aggregate('count', ['C'], [verb])


def level(value):
    if value == 'low':
        return '1'
    elif value == 'medium':
        return '2'
    else:
        return '3'


def change_sign(string):
    signs = {
        '!=': '==',
        '==': '!=',
        '>=': '<',
        '<=': '>',
        '>': '<',
        '<': '>'
    }
    for sign in signs.keys():
        if sign in string:
            string = string.replace(sign, signs[sign])
            break
    return string


def weak_constraint(level, comparison):
    if type(comparison) == Constraint:
        comparison = comparison.body
        for i in range(len(comparison)):
            comparison[i] = change_sign(comparison[i])
    return WeakConstraint(comparison, level, [1])


def simple_clause_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def disjunction_concat(*args):
    res = []
    for arg in args:
        if not isinstance(arg, list):
            arg = [arg]
        res += arg
    return res


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def there_is_clause(entity):
    return Fact(entity)


def math(*args):
    return Aggregate('sum', [args[1][0]], args[1][1:])


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return Constraint([operator.join(map(str, args))])


def comparison_operator(*args):
    items_dict = {'equal to': '!=',
                  'different from': '==',
                  'less than': '>=',
                  'greater than': '<=',
                  'less than or equal to': '>',
                  'greater than or equal to': '<'}
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
    entity = Atom(CnlWizardCompiler.signatures[string_1.lower()])
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def weak_constraint(level, comparison):
    raise NotImplementedError


def level(*args):
    raise NotImplementedError


def word(l_case, string):
    return f'{l_case}{string}'


