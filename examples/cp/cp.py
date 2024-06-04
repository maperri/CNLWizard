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
cnl.support_rule('OPERATOR', '"sum" | "difference" | "division" | "multiplication" | "equal to" | '
                             '"greater than" | "lower than" | "greater than or equal to" | '
                             '"lower than or equal to" | "different from"')


@cnl.rule('OPERATOR')
def operator(arg):
    if arg == 'sum':
        return "+"
    elif arg == 'difference':
        return "-"
    elif arg == 'division':
        return "/"
    elif arg == 'multiplication':
        return "*"
    elif arg == 'equal to':
        return "=="
    elif arg == 'greater than':
        return ">"
    elif arg == 'lower than':
        return "<"
    elif arg == 'greater than or equal to':
        return ">="
    elif arg == 'lower than or equal to':
        return "<="
    elif arg == 'different from':
        return "!="


@cnl.rule('"the" operator "between" comparison_operand "and" comparison_operand')
def comparison_operation(operator, operand_1, operand_2):
    return operand_1, operator, operand_2


cnl.support_rule('comparison_operand', 'number | entity | comparison_operation')


@cnl.rule(
    'comparison_operand ("must be" | "is") operator comparison_operand')
def comparison(operand_1, operator, operand_2):
    comparison = ''
    if isinstance(operand_1, tuple):
        comparison += f'operand_1[0]{operand_1[1]}operand_1[2]'
    else:
        comparison += 'operand_1'
    comparison += operator
    if isinstance(operand_1, tuple):
        comparison += f'operand_2[0]{operand_2[1]}operand_2[2]'
    else:
        comparison += 'operand_2'
    exec(f'model.add({comparison})', globals(), locals())
    return comparison


@cnl.rule('name "equal to" attribute_value')
def attribute(name, attribute_value):
    return name, attribute_value


cnl.support_rule("attributes", '"with" (attribute | entity)', concat=",")


@cnl.rule('("a" | "an")? name attributes')
def entity(name, attributes):
    entity = cnl.signatures[name]
    for name, value in attributes:
        entity.fields[name] = value
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
