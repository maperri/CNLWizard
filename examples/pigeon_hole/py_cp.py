from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler
from ortools.sat.python import cp_model

model = cp_model.CpModel()
vars = {}


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
        entity = model.new_bool_var(str(entity))
        vars[str(entity)] = entity
    return entity


def simple_proposition(entity_1, entity_2):
    field = entity_1.name + '_' + str(list(entity_1.fields.keys())[0])
    entity_2.fields[field] = list(entity_1.fields.values())[0]
    return get_entity_var(entity_1), get_entity_var(entity_2)


def negated_simple_proposition(entity_1, entity_2):
    field = entity_1.name + '_' + str(list(entity_1.fields.keys())[0])
    entity_2.fields[field] = list(entity_1.fields.values())[0]
    return get_entity_var(entity_1), get_entity_var(entity_2).negated()



def entity(string, attribute):
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


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
    return simple_proposition


def disjunction(simple_1, simple_2):
    model.add_bool_or(simple_1[1], simple_2[1])
    return model.add_bool_or(simple_1[1].negated(), simple_2[1].negated())


def consequential(simple_1, simple_2):
    return model.add_bool_or(simple_1[1].negated(), simple_2[1])


def there_is_clause(entity):
    return get_entity_var(entity)
