from CNLWizard.CNLWizard import *


@cnl_type('{self.negation}{self.name}({",".join(self.fields.values())})')
class Atom:
    name: str
    fields: dict
    negation: str


cnl = Cnl(signatures=Signatures(signature_type=Atom))


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


@cnl_type('{self.value1}{self.operator}{self.value2}')
class Comparison:
    operator: str
    value1: str
    value2: str


@cnl_type('{self.lb} {{{self.head}{": " + ", ".join(map(str, self.condition))}}} {self.ub} :- {", ".join(map(str, self.body))}.')
class Choice:
    head: Atom
    body: list
    condition: list
    lb: str
    ub: str


@cnl_type('{" | ".join(map(str, self.head))} :- {", ".join(map(str, self.body))}.')
class Assignment:
    head: list
    body: list


@cnl_type(':~ {", ".join(map(str, self.body))}. [{self.weight}@{", ".join(map(str, self.discriminant))}]')
class WeakConstraint:
    body: list
    weight: int
    discriminant: list

@cnl.rule('"with" attribute_name [("equal to")? attribute_value]')
def parameter(attribute_name, attribute_value):
    return [attribute_name, attribute_value]


cnl.support_rule("parameters", "parameter", concat=',')
cnl.support_rule('entity', 'positive_entity | negative_entity')


@cnl.rule('("a" | "an")? name parameters')
def positive_entity(name, parameters):
    entity = cnl.signatures[name]
    for name, value in parameters:
        entity.fields[name] = value
    return entity


@cnl.rule('"not" entity')
def negative_entity(entity):
    entity.negation = "not "
    return entity


@cnl.rule('"There is " entity')
def fact(entity):
    return Fact(entity)


@cnl.rule('string "is a constant equal to" attribute_value')
def constant(string, attribute_value):
    return Constant(string, attribute_value)


cnl.support_rule('constraint_body',
                 'entity | aggregate | aggregate_comparison | arithmetic_comparison',
                 concat="and")


@cnl.rule('"It is prohibited that there is" constraint_body [whenever_clause]')
def constraint(body, terminal):
    return Constraint(body + terminal) if terminal else Constraint(body)


cnl.support_rule("AGGREGATE_OPERATOR",
    '"the number of" | "the total of" | "the lowest value of" | "the highest value of"')


@cnl.rule('AGGREGATE_OPERATOR')
def aggregate_operator(operator):
    if operator == "the number of":
        return "count"
    elif operator == "the total of":
        return "sum"
    elif operator == "the lowest value of":
        return "min"
    elif operator == "the highest value of":
        return "max"


@cnl.rule('aggregate_operator attribute_name "that" entity')
def aggregate(aggregate_operator, attribute_name, entity):
    parameter_value = entity.fields[attribute_name]
    return Aggregate(aggregate_operator, [parameter_value], [entity])


cnl.support_rule('COMPARISON_OPERATOR',
    '"sum" | "difference" | "equal to" | "different from" | "lower than" | "greater than" | "lower than or equal to" | "greater than or equal to"')


@cnl.rule("COMPARISON_OPERATOR")
def comparison_operator(operator):
    if operator == "sum":
        return "+"
    elif operator == "difference":
        return "-"
    elif operator == "equal to":
        return "="
    elif operator == "different from":
        return "!="
    elif operator == "lower than":
        return "<"
    elif operator == "greater than":
        return ">"
    elif operator == "lower than or equal to":
        return "<="
    elif operator == "greater than or equal to":
        return ">="


@cnl.rule(
    '"the" comparison_operator "between" attribute_value "and" attribute_value "is"? comparison_operator attribute_value')
def arithmetic_comparison(comparison_operator, attribute_value, attribute_value2, comparison_operator2,
                          attribute_value3):
    return Comparison(comparison_operator2, Comparison(comparison_operator, attribute_value, attribute_value2),
                      attribute_value3)


@cnl.rule('aggregate "is" comparison_operator attribute_value')
def aggregate_comparison(aggregate, comparison_operator, attribute_value):
    return Comparison(comparison_operator, aggregate, attribute_value)


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


@cnl.rule("CARDINALITY")
def cardinality(cardinality):
    if cardinality == "exactly one":
        return "1", "1"
    elif cardinality == "at lest one":
        return "1", ""
    elif cardinality == "at most one":
        return "", "1"


cnl.support_rule('LEVEL', '"low" | "medium" | "high"')


@cnl.rule("LEVEL")
def level(level):
    if level == "low":
        return 1
    elif level == "medium":
        return 2
    elif level == "high":
        return 3


@cnl.rule(
    '"It is preferred as much as possible, with" level "priority that" arithmetic_comparison [whenever_clause]')
def weak_constraint(level, arithmetic_comparison, whenever_clause):
    body = [arithmetic_comparison]
    if whenever_clause:
        body += whenever_clause
    return WeakConstraint(body, level, [1])


@cnl.rule("name parameters string")
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