from collections import defaultdict

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def simple_proposition(entity_1, entity_2, entity_3):
    return (entity_1, entity_2, entity_3)


def negated_simple_proposition(entity_1, verb, entity_2):
    return (entity_1, verb, entity_2)


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


def verb(string_1, attribute, string_2):
    entity = CnlWizardCompiler.signatures[string_1]
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


def comparison_operator(*args):
    items_dict = {'equal to': '==', 'different from': '!=', 'less than': '<', 'greater than': '>',
                  'less than or equal to': '<=', 'greater than or equal to': '>='}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    res = []
    for constraint in args[0][1]:
        operation = f'res.append({constraint} {args[1]} {args[2]})'
        exec(operation, locals(), globals())
    return res


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def math(*args):
    return args[1]


domain = defaultdict(list)
vars = set()