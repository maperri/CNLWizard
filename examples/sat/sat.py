from pysat.formula import CNF, Atom, Neg
from sympy.logic.boolalg import to_cnf
from CNLWizard.CNLWizard import CnlWizard, cnl_type, Signatures, CNAME, SIGNED_NUMBER, WHITE_SPACE, WORD


@cnl_type('{self.negation}{self.name}_{"_".join(self.fields.values())}')
class Definition:
    name: str
    fields: dict
    negation: str


@cnl_type('({self.clause})')
class Clause:
    clause: str


@cnl_type('{self.cnf.to_dimacs()}')
class Formula:
    cnf: CNF


cnl = CnlWizard(signatures=Signatures(signature_type=Definition))
cnl.import_token(CNAME)
cnl.import_token(SIGNED_NUMBER)
cnl.ignore_token(WHITE_SPACE)

cnl.support_rule("start", "sat_formula")


@cnl.rule("formula_body")
def sat_formula(formula_body):
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


cnl.support_rule('formula_body', '((constraint | fact | if_then)".")', concat='')


@cnl.rule('"There is" entity')
def fact(entity):
    return Clause(entity)


@cnl.rule('"It is required that" clause_body')
def constraint(clause_body):
    return Clause(clause_body)


cnl.support_rule("clause_body", "there_is_clause | simple_clause | formula")
cnl.support_rule('formula_first', 'clause_body')
cnl.support_rule('formula_second', 'clause_body')


@cnl.rule('"there is" entity')
def there_is_clause(entity):
    return Clause(entity)


@cnl.rule('"If" clause_body ", then" clause_body')
def if_then(clause_body1, clause_body_2):
    return Clause(f'{clause_body1}>>{clause_body_2}')


@cnl.rule('entity [NEGATION] ("is" | "be" | "have" | "has") entity')
def simple_clause(entity1, negation, entity2):
    for key, value in entity1.fields.items():
        field_name = entity1.name + key
        entity2.fields[field_name] = value
    return Clause("~" + str(entity2)) if negation else Clause(str(entity2))


@cnl.extends('[NEGATION] entity')
def entity(negation, entity):
    if negation:
        entity.negation = '~'
    return entity


cnl.support_rule("NEGATION", '"cannot"')
cnl.support_rule('name', 'CNAME')
cnl.support_rule('attribute_value', 'string | NUMBER')
cnl.support_rule('string', 'WORD')
cnl.import_token(WORD)
res = cnl.compile()
print(res)
