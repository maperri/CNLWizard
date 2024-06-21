from z3 import *
from CNLWizard.CNLWizard import CnlWizard, cnl_type, Signatures, CNAME, SIGNED_NUMBER, WHITE_SPACE, WORD, COMMENT


@cnl_type('{self.name}_{"_".join(self.fields.values())}')
class Definition:
    name: str
    fields: dict


cnl = CnlWizard(signatures=Signatures(signature_type=Definition))
cnl.import_token(CNAME)
cnl.import_token(SIGNED_NUMBER)
cnl.ignore_token(WHITE_SPACE)

cnl.support_rule("start", "smt_formula")


@cnl.rule("formula_body")
def smt_formula(formula_body):
    s = Solver()
    for clause in formula_body:
        s.add(clause)
    v = (Ast * 0)()
    a = s.assertions()
    f = And(*a)
    res = Z3_benchmark_to_smtlib_string(f.ctx_ref(), "benchmark", "QF_UFLIA", "unknown", "", 0, v, f.as_ast())
    return f'{res}\n(get-model)'


cnl.support_rule("list_of_strings", 'string', concat=",")
cnl.support_rule('formula_body', 'body', concat="")
cnl.support_rule('body', '((function_definition | constraint | fact | if_then | comparison)".")')


@cnl.rule('("A" | "An") name "is a function which takes" string "and returns" string')
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
    cnl.signatures[name] = f, [], [], ['function', None, None]


@cnl.rule('"There is" entity')
def fact(entity):
    return entity


@cnl.rule('"It is required that" clause_body')
def constraint(clause_body):
    return clause_body


cnl.support_rule("clause_body", "there_is_clause | simple_clause | formula | comparison ")

cnl.support_rule('math_operand', 'entity | NUMBER')
cnl.support_rule('comparison_first', 'math_operation | NUMBER | ("the"i entity)')
cnl.support_rule('comparison_second', 'entity | NUMBER')
cnl.math_operation.compute = True
cnl.comparison.compute = True


@cnl.rule('"there is" entity')
def there_is_clause(entity):
    return entity


cnl.support_rule('formula_first', 'clause_body')
cnl.support_rule('formula_second', 'clause_body')
cnl.formula['or'] = Or
cnl.formula['and'] = And


@cnl.rule('"If" clause_body ", then" clause_body')
def if_then(clause_body1, clause_body_2):
    return If(clause_body1, clause_body_2)


cnl.support_rule("NEGATION", '"cannot"')


@cnl.rule('entity [NEGATION] ("is" | "be" | "have" | "has") entity')
def simple_clause(entity1, negation, entity2):
    for key, value in entity1.fields.items():
        field_name = entity1.name + key
        entity2.fields[field_name] = value
    return Not(entity2) if negation else entity2


cnl.support_rule("attributes", 'attribute | ("with" entity)', concat=",")


@cnl.rule('("a" | "an")? name attributes')
def entity(name, attributes):
    entity = cnl.signatures[name]
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


cnl.support_rule('name', 'CNAME')
cnl.support_rule('attribute_value', 'string | NUMBER')
cnl.support_rule('string', 'WORD')
cnl.import_token(WORD)
cnl.ignore_token(COMMENT)
res = cnl.compile()
print(res)
