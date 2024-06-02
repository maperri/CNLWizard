from z3 import *
from CNLWizard.CNLWizard import Cnl, cnl_type, Signatures, CNAME, SIGNED_NUMBER, WHITE_SPACE, WORD, COMMENT


@cnl_type('{self.name}_{"_".join(self.fields.values())}')
class Definition:
    name: str
    fields: dict


cnl = Cnl(signatures=Signatures(signature_type=Definition))
cnl.import_token(CNAME)
cnl.import_token(SIGNED_NUMBER)
cnl.ignore_token(WHITE_SPACE)

cnl.support_rule("start", "formula")


@cnl.rule("formula_body")
def formula(formula_body):
    s = Solver()
    for clause in formula_body:
        s.add(clause)
    return f'{s.sexpr()}(check-sat)\n(get-model)'


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
    cnl.signatures[name] = f, [], [], 'function'


@cnl.rule('"There is" entity')
def fact(entity):
    return entity


@cnl.rule('"It is required that" clause_body')
def constraint(clause_body):
    return clause_body


cnl.support_rule("clause_body", "there_is_clause | simple_clause | or_operation | and_operation | comparison ")

cnl.support_rule('OPERATOR',
                 '"equal to" | "greater than" | "lower than" | "greater than or equal to" | "lower than or equal to" | "different from" ')


@cnl.rule('("The"|"the") [string "between"] entity ["and" (SIGNED_NUMBER | entity)] ("must be" | "is") OPERATOR (SIGNED_NUMBER | entity)')
def comparison(arith_operator, entity_1, entity_2, eq_operator, res):
    op = None
    if arith_operator == 'sum':
        op = entity_1 + entity_2
    elif arith_operator == 'difference':
        op = entity_1 - entity_2
    elif arith_operator == 'division':
        op = entity_1 / entity_2
    elif arith_operator == 'multiplication':
        op = entity_1 * entity_2
    else:
        op = entity_1
    if eq_operator == 'equal to':
        op = op == res
    elif eq_operator == 'greater than':
        op = op > res
    elif eq_operator == 'lower than':
        op = op < res
    elif eq_operator == 'greater than or equal to':
        op = op >= res
    elif eq_operator == 'lower than or equal to':
        op = op <= res
    elif eq_operator == 'different from':
        op = op != res
    return op


@cnl.rule('"there is" entity')
def there_is_clause(entity):
    return entity


@cnl.rule('clause_body "or" clause_body')
def or_operation(clause_body1, clause_body_2):
    return Or(clause_body1, clause_body_2)


@cnl.rule('clause_body "and" clause_body')
def and_operation(clause_body1, clause_body_2):
    return And(clause_body1, clause_body_2)


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


@cnl.rule('name "equal to" attribute_value')
def attribute(name, attribute_value):
    return name, attribute_value


cnl.support_rule("attributes", '"with" (attribute | entity)', concat=",")

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
cnl.support_rule('attribute_value', 'string | SIGNED_NUMBER')
cnl.support_rule('string', 'WORD')
cnl.import_token(WORD)
cnl.ignore_token(COMMENT)
res = cnl.compile()
print(res)
