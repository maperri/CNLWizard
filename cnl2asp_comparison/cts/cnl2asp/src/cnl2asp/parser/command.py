from cnl2asp.parser.proposition_builder import PropositionBuilder
from cnl2asp.specification.attribute_component import ValueComponent, AttributeComponent
from cnl2asp.specification.entity_component import EntityComponent
from cnl2asp.specification.operation_component import OperationComponent, Operators
from cnl2asp.specification.problem import Problem
from cnl2asp.specification.proposition import NewKnowledgeComponent
from cnl2asp.specification.signaturemanager import SignatureManager


class Command:
    def execute(self):
        return

class DurationClause(Command):
    def __init__(self, proposition: PropositionBuilder, new_knowledge: NewKnowledgeComponent,
                 duration_value: ValueComponent, attribute_name: str):
        self.proposition = proposition
        self.new_knowledge = new_knowledge
        self.duration_value = duration_value
        self.attribute_name = attribute_name

    def execute(self):
        self.proposition.duration_clause(self.new_knowledge, self.duration_value, self.attribute_name)


class CreateSignature(Command):
    def __init__(self, proposition: PropositionBuilder, entity: EntityComponent):
        self.proposition = proposition
        self.entity = entity

    def execute(self):
        try:
            signature = SignatureManager.clone_signature(self.entity.get_name())
        except:
            signature = self.proposition.create_new_signature(self.entity)
            SignatureManager.add_signature(signature)
        signature.set_attributes_value(self.entity.get_keys_and_attributes())
        self.entity.keys = signature.keys
        self.entity.attributes = signature.attributes
