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
    for key, value in entity.fields.items():
        domain[f'{entity.name}_{key}'].append(value)


def math(*args):
    return args[1]


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    res = []
    for constraint in args[0][1]:
        operation = f'res.append({constraint} {args[1]} {args[2]})'
        exec(operation, locals(), globals())
    return res


def comparison_operator(*args):
    items_dict = {'equal to': '==', 'different from': '!=', 'less than': '<', 'greater than': '>',
                  'less than or equal to': '<=', 'greater than or equal to': '>='}
    item = ' '.join(args)
    return items_dict[item]


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


def verb(string_1, attribute, string_2):
    entity = CnlWizardCompiler.signatures[string_1]
    if attribute:
        for name, value in attribute:
            entity.fields[name] = value
    return entity


