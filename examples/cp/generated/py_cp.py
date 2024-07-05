from ortools.sat.python import cp_model

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler

model = cp_model.CpModel()
vars = {}


def start(*constraint):
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    solution = ''
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for var in vars.values():
            solution += f"{var} = {solver.value(var)}\n"
    else:
        solution += "No solution found."
    return solution


def math_operator(*args):
    items_dict = {'sum': '+', 'difference': '-', 'division': '/', 'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def math(*args):
    operator_index = 0
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    ns = {}
    for i in range(len(args)):
        if isinstance(args[i], str):
            args[i] = int(args[i])
    operands = [f'args[{i}]' for i in range(len(args))]
    exec(f'res={operator.join(operands)}', locals(), ns)
    return ns['res']


def comparison_operator(*args):
    items_dict = {'equal to': '==', 'different from': '!=', 'lower than': '<', 'greater than': '>',
                  'lower than or equal to': '<=', 'greater than or equal to': '>='}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    ns = {}
    operands = [f'args[{i}]' for i in range(len(args))]
    exec(f'res={operator.join(operands)}', locals(), ns)
    model.add(ns['res'])
    return ns['res']


def entity(name, attributes):
    entity = CnlWizardCompiler.signatures[name]
    for name, value in attributes:
        entity.fields[name] = value
    if str(entity) in vars:
        return vars[str(entity)]
    if entity.type == 'integer':
        entity = model.new_int_var(entity.lb, entity.ub, str(entity))
        vars[str(entity)] = entity
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
