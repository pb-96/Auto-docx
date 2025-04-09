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

    def build_prompt(self):
        # Should return testable -> parent -> description -> parent -> description etc...
        testable_target = [*find_testable_ticket(self.ticket_tree)]
        if not all((is_leaf(ticket) for ticket in testable_target)):
            raise ValueError("Testable target is not a leaf")

        ticket_tree_structure = self.ticket_tree.display_relationship()
        parent_ticket_type = self.ticket_tree.ticket_type
        ticket_descriptions = {}
        parent_key = next(iter(self.ticket_ingester.types_to_keys[parent_ticket_type]))
        parent_description = self.ticket_ingester.formatted_tree[parent_key]
        ticket_descriptions[parent_ticket_type] = parent_description

        # This should be done for evert ticket that is a leaf and testable
        for_prompt_builder = {
            "tree_structure": ticket_tree_structure,
            "parent_ticket_type": parent_ticket_type,
            "child_ticket_type": testable_target[0].ticket_type,
            "ticket_descriptions": ticket_descriptions,
            "desired_format": "celery",
            "python_version": "3.11",
            "test_name": "prompt_test",
        }

        prompt = build_test_builder_prompt(for_prompt_builder)
        return prompt
