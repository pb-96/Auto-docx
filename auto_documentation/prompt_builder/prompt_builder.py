from auto_documentation.prompt_builder.prompts import build_test_builder_prompt
from auto_documentation.ticket_ingestion.configs.ticket_tree import TicketTree
from auto_documentation.ticket_ingestion.ticket_ingestor_base import GenericIngester
from auto_documentation.ticket_ingestion.configs.jira_config import JiraConfig
from auto_documentation.utils import find_testable_ticket, is_leaf
from collections import deque


class PromptBuilder:
    def __init__(
        self,
        parent_ticket_id: str,
        ticket_tree: TicketTree,
        ticket_ingester: GenericIngester,
        generic_config: JiraConfig,
    ):
        self.prompt = {}
        self.parent_ticket_id = parent_ticket_id
        self.ticket_tree = ticket_tree
        self.generic_config = generic_config
        self.ticket_ingester = ticket_ingester(
            self.generic_config, self.ticket_tree, self.parent_ticket_id
        )

    def get_ticket_description(self, child_key: str, parent_key: str):
        ticket_descriptions = {}
        upward_order = [child_key]
        lookup = child_key
        while lookup != parent_key:
            metadata = self.ticket_ingester.formatted_tree[lookup]
            ticket_descriptions[lookup] = metadata["description"]
            lookup = metadata["parent_key"]
            upward_order.append(lookup)

        ticket_descriptions[parent_key] = self.ticket_ingester.formatted_tree[
            parent_key
        ]["description"]
        upward_order.append(parent_key)
        upward_order.reverse()
        return ticket_descriptions, upward_order

    def build_prompt(self):
        # Should return testable -> parent -> description -> parent -> description etc...
        testable_target = [*find_testable_ticket(self.ticket_tree)]
        if not all((is_leaf(ticket) for ticket in testable_target)):
            raise ValueError("Testable target is not a leaf")

        ticket_tree_structure = self.ticket_tree.display_relationship()
        parent_ticket_type = self.ticket_tree.ticket_type
        parent_key = self.ticket_ingester.types_to_keys[parent_ticket_type]
        assert len(parent_key) == 1
        parent_key = next(iter(parent_key))

        for ticket in testable_target:
            for child_key in self.ticket_ingester.types_to_keys[ticket.ticket_type]:
                ticket_descriptions, upward_order = self.get_ticket_description(
                    child_key, parent_key
                )
                print(ticket_descriptions, upward_order)
                # Parse ticket descriptions
                for_prompt_builder = {
                    "tree_structure": ticket_tree_structure,
                    "parent_ticket_type": parent_ticket_type,
                    "child_ticket_type": ticket.ticket_type,
                    "ticket_descriptions": ticket_descriptions,
                    "desired_format": "celery",
                    "python_version": "3.11",
                    "test_name": "prompt_test",
                }

                build_test_builder_prompt(for_prompt_builder)
