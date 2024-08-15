import copy
from collections import defaultdict

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler
from ortools.sat.python import cp_model

model = cp_model.CpModel()
vars = {}
domain = defaultdict(list)


def start(*proposition):
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    solution = ''
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for var in vars.values():
            solution += f"{var} = {solver.value(var)}\n"
    else:
        solution += "No solution found."
    return solution


def get_entity_var(entity):
    if str(entity) in vars:
        entity = vars[str(entity)]
    else:
        entity = model.new_int_var(0, 1, str(entity))
        vars[str(entity)] = entity
    return entity


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
    return model.add(get_entity_var(simple_1[0]) + get_entity_var(simple_2) == 1)


def there_is_clause(entity):
    for key, value in entity.fields.items():
        domain[f'{entity.name}_{key}'].append(value)
    return get_entity_var(entity)


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
    for constraint in args[0][1]:
        operation = f'model.add({constraint} {args[1]} {args[2]})'
        exec(operation, locals(), globals())
    return operation


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def math(*args):
    return args[1]


def math_first(string, entity_1, verb, entity_2):
    field_1_name = f'{entity_1.name}_{list(CnlWizardCompiler.signatures[entity_1.name].fields.keys())[0]}'
    field_1_values = domain[field_1_name]
    field_2_name = f'{entity_2.name}_{list(CnlWizardCompiler.signatures[entity_2.name].fields.keys())[0]}'
    field_2_values = domain[field_2_name]
    operations = []
    for value2 in field_2_values:
        curr = []
        for value1 in field_1_values:
            tmp = copy.deepcopy(verb)
            tmp.fields[field_1_name] = value1
            tmp.fields[field_2_name] = value2
            curr.append(tmp)
        operations.append(curr)
    res = []
    for operation in operations:
        curr = ''
        for i in range(len(operation)):
            curr += f'get_entity_var(args[0][0][{len(res)}][{i}]) * {domain[f"{entity_1.name}_{string}"][i]} + '
        curr = curr.removesuffix('+ ')
        res.append(curr)
    return operations, res


def comparison_first(math):
    return math


def comparison_second(number):
    return number


def aggregate(entity_1, verb, entity_2):
    field_1_name = f'{entity_1.name}_{list(CnlWizardCompiler.signatures[entity_1.name].fields.keys())[0]}'
    field_1_values = domain[field_1_name]
    field_2_name = f'{entity_2.name}_{list(CnlWizardCompiler.signatures[entity_2.name].fields.keys())[0]}'
    field_2_values = domain[field_2_name]
    operations = []
    for value2 in field_2_values:
        curr = []
        for value1 in field_1_values:
            tmp = copy.deepcopy(verb)
            tmp.fields[field_1_name] = value1
            tmp.fields[field_2_name] = value2
            curr.append(tmp)
        operations.append(curr)
    res = []
    for operation in operations:
        curr = ''
        for i in range(len(operation)):
            curr += f'get_entity_var(args[0][0][{len(res)}][{i}]) + '
        curr = curr.removesuffix('+ ')
        res.append(curr)
    return operations, res


def negated_simple_proposition(entity_1, verb, entity_2):
    return (entity_1, verb, entity_2)
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


