from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler
from ortools.sat.python import cp_model
from collections import defaultdict


def simple_proposition(entity_1, entity_2, entity_3):
    return (entity_1, entity_2, entity_3)


def entity(string, attribute):
    entity = CnlWizardCompiler.signatures[string.lower().removesuffix('s')]
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def attribute(name, attribute_value):
    return [(name, attribute_value)]


def there_is_clause(entity):
    for key, value in entity.fields.items():
        domain[f'{entity.name}_{key}'].append(value)
    return get_entity_var(entity)


def get_entity_var(entity):
    if str(entity) in vars:
        entity = vars[str(entity)]
    else:
        entity = model.new_int_var(0, 1, str(entity))
        vars[str(entity)] = entity
    return entity


def negated_simple_proposition(entity_1, verb, entity_2):
    return (entity_1, verb, entity_2)


def math(*args):
    return args[1]


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    for constraint in args[0][1]:
        operation = f'model.add({constraint} {args[1]} {args[2]})'
        exec(operation, locals(), globals())
    return operation


def comparison_operator(*args):
    items_dict = {'equal to': '==', 'different from': '!=', 'less than': '<', 'greater than': '>',
                  'less than or equal to': '<=', 'greater than or equal to': '>='}
    item = ' '.join(args)
    return items_dict[item]


def verb(string_1, attribute, string_2):
    entity = CnlWizardCompiler.signatures[string_1]
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity

model = cp_model.CpModel()
vars = {}
domain = defaultdict(list)
