from CNLWizard.CNLWizard import *


@cnl_type('{self.negation}{self.name}({",".join(self.fields.values())})')
class Atom:
    name: str
    fields: dict
    negation: str


cnl = CnlWizard(signatures=Signatures(signature_type=Atom))


@cnl_type('{self.head}.')
class Fact:
    head: Atom


@cnl_type('#const {self.name}={self.value}.')
class Constant:
    name: str
    value: str


@cnl_type(':- {", ".join(map(str, self.atoms))}.')
class Constraint:
    atoms: list


@cnl_type('#{self.operator}{{{", ".join(map(str, self.discriminant))}: {", ".join(map(str, self.body))}}}')
class Aggregate:
    operator: str
    discriminant: list
    body: list


@cnl_type()
class Choice:
    head: Atom
    body: list
    condition: list
    lb: str
    ub: str

    def __str__(self):
        head_cond = ": " + ", ".join(map(str, self.condition)) if self.condition else ''
        return f'{self.lb} {{{self.head}{head_cond}}} {self.ub} :- {", ".join(map(str, self.body))}.'


@cnl_type('{" | ".join(map(str, self.head))} :- {", ".join(map(str, self.body))}.')
class Assignment:
    head: list
    body: list


@cnl_type(':~ {", ".join(map(str, self.body))}. [{self.weight}@{", ".join(map(str, self.discriminant))}]')
class WeakConstraint:
    body: list
    weight: int
    discriminant: list


cnl.support_rule('NEGATION', '"not"')


@cnl.extends('[NEGATION] entity')
def entity(negation, entity):
    if negation:
        entity.negation = 'not '
    return entity


@cnl.rule('"There is " entity')
def fact(entity):
    return Fact(entity)


@cnl.rule('string "is a constant equal to" attribute_value')
def constant(string, attribute_value):
    return Constant(string, attribute_value)


cnl.support_rule('constraint_body', 'entity | aggregate | comparison', concat="and")


@cnl.rule('"It is prohibited that there is" constraint_body [whenever_clause]')
def constraint(body, terminal):
    return Constraint(body + terminal) if terminal else Constraint(body)


cnl.support_rule("AGGREGATE_OPERATOR",
                 '"the number of" | "the total of" | "the lowest value of" | "the highest value of"')

cnl.support_rule('aggregate_operator', {
    "the number of": "count",
    "the total of": "sum",
    "the lowest value of": "min",
    "the highest value of": "max"
})


@cnl.rule('aggregate_operator attribute_name "that" entity')
def aggregate(aggregate_operator, attribute_name, entity):
    parameter_value = entity.fields[attribute_name]
    return Aggregate(aggregate_operator, [parameter_value], [entity])


cnl.support_rule('comparison_second', 'attribute_value')
cnl.support_rule('comparison_first', 'math_operation | aggregate')
cnl.support_rule('math_operand', 'attribute_value')
cnl.support_rule("then_subject", "entity | verb")
cnl.support_rule("then_object", 'then_subject', concat=",")


@cnl.rule('whenever_clause ", then we can have" [cardinality] then_subject [then_object]')
def whenever_then_clause_choice(whenever_clause, cardinality, then_subject, then_object):
    whenever_then_clause_choice = Choice(then_subject, whenever_clause, then_object)
    if cardinality:
        whenever_then_clause_choice.lb = cardinality[0]
        whenever_then_clause_choice.ub = cardinality[1]
    return whenever_then_clause_choice


cnl.support_rule('disjunction_then_subject', 'then_subject', concat="or")


@cnl.rule(
    'whenever_clause ", then we must have" then_subject | whenever_clause ", then we can have" disjunction_then_subject ')
def whenever_then_clause_assignment(whenever_clause, subject):
    return Assignment([subject], whenever_clause)


cnl.support_rule('CARDINALITY', '"exactly one" | "at lest one" | "at most one"')

cnl.support_rule('cardinality', {
    'exactly one': ('1', '1'),
    'at least one': ('1', ''),
    'at most one': ('', '1')
})

cnl.support_rule('level', {
    'low': 1,
    'medium': 2,
    'high': 3,
})


@cnl.rule(
    '"It is preferred as much as possible, with" level "priority that" comparison [whenever_clause]')
def weak_constraint(level, arithmetic_comparison, whenever_clause):
    body = [arithmetic_comparison]
    if whenever_clause:
        body += whenever_clause
    return WeakConstraint(body, level, [1])


@cnl.rule("name attributes string")
def verb(name, parameters, string):
    verb = cnl.signatures[name + string]
    for parameter in parameters:
        verb.fields[parameter[0]] = parameter[1]
    return verb


cnl.support_rule("whenever_clause", '("whenever there is" | "Whenever there is") entity', concat=",")

cnl.support_rule("start",
                 '((fact | constant | constraint | whenever_then_clause_choice | whenever_then_clause_assignment | weak_constraint) ".")+')

cnl.import_token(WORD)
cnl.import_token(SIGNED_NUMBER)
cnl.support_rule("name", "CNAME")
cnl.support_rule("attribute_name", "CNAME")
cnl.support_rule("attribute_value", "string | SIGNED_NUMBER")
cnl.support_rule("string", "WORD")

parser = argparse.ArgumentParser()
parser.add_argument('input_file')
args = parser.parse_args()
specification = open(args.input_file, 'r').read()
res = cnl.compile(specification)
print(res)
