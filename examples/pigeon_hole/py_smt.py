from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler
from z3 import IntSort, BoolSort, Function, If, Solver, Z3_benchmark_to_smtlib_string, And, Ast, Not, Or, Bool, Int, \
    Implies


def start(*proposition):
    s = Solver()
    for clause in proposition:
        s.add(clause)
    v = (Ast * 0)()
    a = s.assertions()
    f = And(*a)
    res = Z3_benchmark_to_smtlib_string(f.ctx_ref(), "benchmark", "QF_UFLIA", "unknown", "", 0, v, f.as_ast())
    return f'{res}\n(get-model)'


def simple_proposition(entity_1, entity_2):
    field = entity_1.name + '_' + str(list(entity_1.fields.keys())[0])
    entity_2.fields[field] = list(entity_1.fields.values())[0]
    return Bool(str(entity_1)), Bool(str(entity_2))


def negated_simple_proposition(entity_1, entity_2):
    field = entity_1.name + '_' + str(list(entity_1.fields.keys())[0])
    entity_2.fields[field] = list(entity_1.fields.values())[0]
    return Bool(str(entity_1)), Not(Bool(str(entity_2)))


def positive_constraint(positive_constraint_body):
    return positive_constraint_body


def entity(string, attribute):
    from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler
    entity = CnlWizardCompiler.signatures[string]
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


def proposition(positive_constraint):
    return positive_constraint


def positive_constraint_body(simple_clause):
    return simple_clause


def simple_clause(simple_proposition):
    return simple_proposition


def disjunction(simple_1, simple_2):
    return Implies(simple_1[0], And(Or(simple_1[1], simple_2[1]), Or(Not(simple_1[1]), Not(simple_2[1]))))


def consequential(simple_1, simple_2):
    return Implies(simple_1[1], simple_2[1])


def there_is_clause(entity):
    return Bool(str(entity))

