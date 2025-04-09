from auto_documentation.ticket_tree.ticket_tree import TicketTree
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
        ...

    def build_prompt(self):
        # Should return testable -> parent -> description -> parent -> description etc...
        testable_target = [*find_testable_ticket(self.ticket_tree)]
        if not all((is_leaf(ticket) for ticket in testable_target)):
            raise ValueError("Testable target is not a leaf")
        

