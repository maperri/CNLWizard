from pysat.formula import CNF

from CNLWizard.CNLWizard import Cnl, cnl_type, Signatures, CNAME, SIGNED_NUMBER, WHITE_SPACE, WORD


@cnl_type('{self.name}_{"_".join(self.fields.values())}')
class Definition:
    name: str
    fields: dict


@cnl_type('{self.clause}')
class Clause:
    clause: str


@cnl_type('{self.cnf.to_dimacs()}')
class Formula:
    cnf: CNF


cnl = Cnl(signatures=Signatures(signature_type=Definition))
cnl.import_token(CNAME)
cnl.import_token(SIGNED_NUMBER)
cnl.ignore_token(WHITE_SPACE)

cnl.support_rule("start", "formula")


@cnl.rule("formula_body")
def formula(formula_body):
    from sympy.logic.boolalg import to_cnf
    from pysat.formula import Atom
    from pysat.formula import Neg
    formula_body = "&".join(["(" + str(x) + ")" for x in formula_body])
    formula_body = str(to_cnf(formula_body))
    definitions = []
    formula = Formula()
    for clause in formula_body.split("&"):
        literals = []
        for atom in clause.split("|"):
            atom_name = atom.strip().removeprefix("(").removesuffix(")")
            is_negated = atom_name.startswith("~")
            atom_name = atom_name.removeprefix("~")
            literal = Atom(atom_name)
            if is_negated:
                literal = Neg(literal)
                literal.clausify()
                literals.append(literal.clauses[0][0])
            else:
                literal.clausify()
                literals.append(literal.name)
            if atom_name not in definitions:
                literal_name = literal.name if not is_negated else abs(literal.clauses[0][0])
                formula.cnf.comments.append("c " + str(literal_name) + " " + atom_name)
                definitions.append(atom_name)
        formula.cnf.append(literals)
    return formula


cnl.support_rule("list_of_strings", 'string', concat=",")
cnl.support_rule('formula_body', 'body', concat="")

cnl.support_rule('body', '((constraint | fact | if_then)".")')


@cnl.rule('"There is" entity')
def fact(entity):
    return Clause(entity)


@cnl.rule('"It is required that" clause_body')
def constraint(clause_body):
    return Clause(clause_body)


cnl.support_rule("clause_body", "there_is_clause | simple_clause | or_operation | and_operation")


@cnl.rule('"there is" entity')
def there_is_clause(entity):
    return Clause(entity)


@cnl.rule('clause_body "or" clause_body')
def or_operation(clause_body1, clause_body_2):
    return Clause(f'({clause_body1}|{clause_body_2})')


@cnl.rule('clause_body "and" clause_body')
def and_operation(clause_body1, clause_body_2):
    return Clause(f'({clause_body1}&{clause_body_2})')


@cnl.rule('"If" clause_body ", then" clause_body')
def if_then(clause_body1, clause_body_2):
    return Clause(f'({clause_body1}>>{clause_body_2})')


cnl.support_rule("NEGATION", '"cannot"')


@cnl.rule('entity [NEGATION] ("is" | "be" | "have" | "has") entity')
def simple_clause(entity1, negation, entity2):
    for key, value in entity1.fields.items():
        field_name = entity1.name + key
        entity2.fields[field_name] = value
    return Clause("~" + str(entity2)) if negation else Clause(str(entity2))


@cnl.rule('"with" name "equal to" attribute_value')
def attribute(name, attribute_value):
    return name, attribute_value


cnl.support_rule("attributes", "attribute", concat=",")
cnl.support_rule("entity", "positive_entity | negative_entity")


@cnl.rule('("a" | "an")? name attributes')
def positive_entity(name, attributes):
    entity = cnl.signatures[name]
    for name, value in attributes:
        entity.fields[name] = value
    return entity


@cnl.rule('"not" positive_entity')
def negative_entity(entity):
    entity.negation = "~"
    return entity


cnl.support_rule('name', 'CNAME')
cnl.support_rule('attribute_value', 'string | NUMBER')
cnl.support_rule('string', 'WORD')
cnl.import_token(WORD)
res = cnl.compile()
print(res)
