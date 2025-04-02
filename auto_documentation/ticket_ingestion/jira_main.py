from typing import Dict
from jira import JIRA
from auto_documentation.ticket_ingestion.configs.jira_config import JiraConfig
from auto_documentation.ticket_ingestion.configs.ticket_tree import TicketTree


class IngestJira:
    def __init__(
        self, jira_config: JiraConfig, ticket_tree: TicketTree, parent_ticket_id: str
    ):
        self.jira_config = jira_config
        self.jira_object = JIRA()
        self.ticket_tree = ticket_tree

    def perform_auth(self):
        email, auth = self.jira_config.email, self.jira_config.auth

    def build_ticket_queries(self): ...

    def get_issues(self): ...
