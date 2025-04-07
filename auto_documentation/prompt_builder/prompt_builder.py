from auto_documentation.ticket_tree.ticket_tree import TicketTree
from typing import Generic

class PromptBuilder:
    def __init__(self, project_id: str, ticket_tree: TicketTree, ticket_ingestor: Generic["V"]):
        self.prompt = {}
        self.project_id = project_id
        self.ticket_tree = ticket_tree
    