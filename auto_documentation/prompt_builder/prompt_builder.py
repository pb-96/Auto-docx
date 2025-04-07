from auto_documentation.ticket_tree.ticket_tree import TicketTree
from auto_documentation.ticket_ingestion.ticket_ingestor_base import GenericIngester
from auto_documentation.ticket_ingestion.configs.jira_config import JiraConfig

class PromptBuilder:
    # TODO: Add a generic config when notion or other sources are supported
    def __init__(self, parent_ticket_id: str, ticket_tree: TicketTree, ticket_ingester: GenericIngester, generic_config: JiraConfig):
        self.prompt = {}
        self.parent_ticket_id = parent_ticket_id
        self.ticket_tree = ticket_tree
        self.generic_config = generic_config
        self.ticket_ingester = ticket_ingester(self.generic_config, self.ticket_tree, self.parent_ticket_id)
 
    def build_prompt(self):
        # Should return testable -> parent -> description -> parent -> description etc...
        return_dict = {}





    