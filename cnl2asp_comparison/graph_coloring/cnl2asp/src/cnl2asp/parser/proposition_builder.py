from cnl2asp.exception.cnl2asp_exceptions import EntityNotFound, LabelNotFound
from cnl2asp.specification.relation_component import RelationComponent
from cnl2asp.specification.attribute_component import AttributeComponent, ValueComponent, RangeValueComponent
from cnl2asp.specification.component import Component
from cnl2asp.specification.entity_component import EntityComponent
from cnl2asp.specification.proposition import Proposition, NewKnowledgeComponent, CardinalityComponent, \
    PreferenceProposition, PREFERENCE_PROPOSITION_TYPE, ConditionComponent
from cnl2asp.utility.utility import Utility


class PropositionBuilder:

    def __init__(self, proposition: Proposition = None):
        self._original_rule: Proposition = proposition if proposition else Proposition()
        self._derived_rules: list[Proposition] = []

    def get_propositions(self) -> list[Proposition]:
        return [self._original_rule] + self._derived_rules

    def get_cardinality(self):
        return self._original_rule.cardinality

    def get_entity_by_label(self, label: str) -> EntityComponent:
        for entity in self._original_rule.get_entities():
            if entity.label == label:
                return entity
        raise LabelNotFound(f"Label \"{label}\" not declared before.")


    def copy_proposition(self) -> Proposition:
        child = self._original_rule.copy()
        self._derived_rules.append(child)
        return child

    def add_cardinality(self, cardinality: CardinalityComponent):
        for proposition in self.get_propositions():
            proposition.cardinality = cardinality

    def add_requisite(self, component: Component):
        for proposition in self.get_propositions():
            proposition.requisite.components.append(component)

    def add_requisite_list(self, component: list[Component]):
        for proposition in self.get_propositions():
            proposition.requisite.components += component

    def add_new_knowledge(self, new_knowledge: NewKnowledgeComponent):
        for proposition in self.get_propositions():
            proposition.new_knowledge.append(new_knowledge)

    def add_relations(self, relations: list[RelationComponent]):
        for proposition in self.get_propositions():
            proposition.relations += relations

    def create_new_signature(self, new_entity: EntityComponent) -> EntityComponent:
        return self._original_rule.create_new_signature(new_entity)

    def add_discriminant(self, discriminant: list[AttributeComponent]):
        pass

    def add_defined_attributes(self, defined_attributes: list[AttributeComponent]):
        for proposition in self.get_propositions():
            proposition.defined_attributes += defined_attributes

    def add_subject(self, param):
        for new_knowledge in self._original_rule.new_knowledge:
            new_knowledge.subject = param


