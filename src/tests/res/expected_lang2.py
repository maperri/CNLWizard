from CNLWizard.cnl_wizard_compiler import CnlWizardCompiler


def start(arithmetic):
    raise NotImplementedError


CnlWizardCompiler.config['signatures'] = False


def arithmetic(*args):
    raise NotImplementedError


def constraint(arithmetic):
    raise NotImplementedError


def entity(string, attribute):
    try:
        entity = CnlWizardCompiler.signatures[string]
        for name, value in attribute:
            entity.fields[name] = value
        return entity
    except KeyError:
        return None


def sum(operand_1, operand_2):
    raise NotImplementedError


def test_operation_operator(*args):
    items_dict = {'sum': sum(operand_1, operand_2)}
    item = ' '.join(args)
    return items_dict[item]


def test_operation(*args):
    operator_index = 0
    operator = args[operator_index]
    args = list(args)
    args.pop(operator_index)
    return operator(*args)


def operation(test_operation):
    raise NotImplementedError


def operand(number):
    raise NotImplementedError


