from ortools.sat.python import cp_model
from CNLWizard.CNLWizard import Cnl, cnl_type, Signatures, CNAME, SIGNED_NUMBER, WHITE_SPACE, WORD, COMMENT, NUMBER


@cnl_type('{self.name}_{"_".join(map(str,self.fields.values()))}')
class Definition:
    name: str
    fields: dict


cnl = Cnl(signatures=Signatures(signature_type=Definition))
cnl.import_token(CNAME)
cnl.import_token(SIGNED_NUMBER)
cnl.ignore_token(WHITE_SPACE)

cnl.support_rule("start", "formula")
model = cp_model.CpModel()


@cnl.rule("formula_body")
def formula(formula_body):
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    solution = ''
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for var in cnl.vars.values():
            solution += f"{var} = {solver.value(var)}\n"
    else:
        solution += "No solution found."
    return solution


cnl.support_rule("list_of_strings", 'string', concat=",")
cnl.support_rule('formula_body', 'body', concat="")
cnl.support_rule('body', '((constraint)".")')
cnl.support_rule('constraint', '"It is required that" comparison')
cnl.math_operation.compute = True
cnl.comparison.compute = True

@cnl.extends('comparison')
def comparison(comparison):
    model.add(comparison)
    return comparison

cnl.support_rule('math_operand', 'number | entity')
cnl.support_rule('comparison_first', 'number | entity | math_operation')
cnl.support_rule('comparison_second', 'number | entity | math_operation')

@cnl.extends('entity')
def entity(entity):
    if str(entity) in cnl.vars:
        return cnl.vars[str(entity)]
    if entity.type == 'integer':
        entity = model.new_int_var(entity.lb, entity.ub, str(entity))
        cnl.vars[str(entity)] = entity
    return entity


@cnl.rule('NUMBER')
def number(num):
    return int(num)


cnl.support_rule('name', 'CNAME')
cnl.support_rule('attribute_value', 'string | number')
cnl.support_rule('string', 'WORD')
cnl.import_token(WORD)
cnl.ignore_token(COMMENT)
res = cnl.compile()
print(res)
