from cnl2asp.ASP_elements.asp_atom import ASPAtom
from cnl2asp.ASP_elements.asp_element import ASPElement
from cnl2asp.ASP_elements.asp_attribute import ASPAttribute
from cnl2asp.ASP_elements.asp_conjunction import ASPConjunction
from cnl2asp.specification.aggregate_component import AggregateOperation


class ASPAggregate(ASPElement):
    symbols = {
        AggregateOperation.SUM: 'sum',
        AggregateOperation.COUNT: 'count',
        AggregateOperation.MAX: 'max',
        AggregateOperation.MIN: 'min'
    }

    def __init__(self, operation: AggregateOperation, discriminant: list[ASPAttribute], body: ASPConjunction):
        self.operation: AggregateOperation = operation
        self.discriminant = discriminant
        self.body = body

    def __str__(self) -> str:
        return f'#{ASPAggregate.symbols[self.operation]}{{' \
               f'{",".join([str(x) for x in self.discriminant])}' \
               f': {str(self.body)}}}'
