from z3 import IntSort, BoolSort, Function, If, Solver, Z3_benchmark_to_smtlib_string, And, Ast, Not, Or, Bool, Int

from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def function_definition(name, arg_sort, return_sort):
    arg = None
    if arg_sort == 'integer':
        arg = IntSort()
    elif arg_sort == 'boolean':
        arg = BoolSort()
    return_s = None
    if return_sort == 'integer':
        return_s = IntSort()
    elif return_sort == 'boolean':
        return_s = BoolSort()
    f = Function(name, arg, return_s)
    CnlWizardCompiler.signatures[name] = f, [], [], ['function', None, None]


def constraint(clause_body):
    return clause_body


def there_is_clause(entity):
    return entity


def if_then(clause_body, clause_body_2):
    return If(clause_body, clause_body_2)


def start(*formula_body):
    s = Solver()
    for clause in formula_body:
        s.add(clause)
    v = (Ast * 0)()
    a = s.assertions()
    f = And(*a)
    res = Z3_benchmark_to_smtlib_string(f.ctx_ref(), "benchmark", "QF_UFLIA", "unknown", "", 0, v, f.as_ast())
    return f'{res}\n(get-model)'


def simple_clause(entity, negation, entity_2):
    for key, value in entity.fields.items():
        field_name = entity.name + key
        entity_2.fields[field_name] = value
    return Not(entity_2) if negation else entity_2


def negation(*args):
    return True


def math_operator(*args):
    items_dict = {'sum': '+',
                  'difference': '-',
                  'division': '/',
                  'multiplication': '*'}
    item = ' '.join(args)
    return items_dict[item]


def math(*args):
    operator_index = 0
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    ns = {}
    operands = [f'args[{i}]' for i in range(len(args))]
    exec(f'res = {operator.join(operands)}', locals(), ns)
    return ns['res']


def formula_operator(*args):
    items_dict = {'and': And,
                  'or': Or,
                  'imply': If,
                  'implies': If,
                  'is equivalent to': '==',
                  'not': Not}
    item = ' '.join(args)
    return items_dict[item]


def formula(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    if operator != '==':
        return operator(*args)
    else:
        return args[0] == args[1]


def attribute(name, attribute_value):
    return name, attribute_value


def entity(name, attributes):
    entity = CnlWizardCompiler.signatures[name]
    if entity.type == 'function':
        f = entity.name
        return f(attributes[0])
    for name, value in attributes:
        entity.fields[name] = value
    if entity.type == 'boolean':
        return Bool(str(entity))
    elif entity.type == 'integer':
        return Int(str(entity))
    return entity


def comparison_operator(*args):
    items_dict = {'different from': '!=',
                  'lower than': '<',
                  'greater than': '>',
                  'lower than or equal to': '<=',
                  'greater than or equal to': '>='}
    item = ' '.join(args)
    return items_dict[item]


def comparison(*args):
    operator_index = 1
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    ns = {}
    operands = [f'args[{i}]' for i in range(len(args))]
    exec(f'res = {operator.join(operands)}', locals(), ns)
    return ns['res']


def propositions(function_definition):
    return function_definition


def clause_body(there_is_clause):
    return there_is_clause


def comparison_operand(math):
    return math


def math_operand(entity):
    return entity


def attributes(*attribute):
   return attribute


def conjunction(*args):
    return And(*args)


def disjunction(*args):
    return Or(*args)


def implication(*args):
    return If(*args)


def equivalence(*args):
    return args[0] == args[1]


def negation_op(*args):
    return Not(*args)


