from typing import Dict, Any
from jira import JIRA
from auto_documentation.ticket_ingestion.configs.jira_config import JiraConfig
from auto_documentation.ticket_ingestion.configs.ticket_tree import TicketTree


class IngestJira:
    def __init__(
        self, jira_config: JiraConfig, ticket_tree: TicketTree, parent_ticket_id: str
    ):
        self.jira_config = jira_config
        self.ticket_tree = ticket_tree
        self.formatted_tree: Dict[str, Any] = {}

    def do_auth(self):
        self.jira = JIRA(
            server=self.jira_config.project_url,
            basic_auth=(self.jira_config.email, self.jira_config.auth),
        )

    def build_ticket_queries(self, ticket_tree: TicketTree):
        jql_query = f'project="{self.jira_config.project_name}" AND summary~"{ticket_tree.ticket_name}" AND issuetype="{ticket_tree.ticket_type}"'
        return jql_query

    def get_issues(self): ...
