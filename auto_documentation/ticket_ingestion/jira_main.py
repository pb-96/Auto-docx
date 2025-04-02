from typing import Dict, Any, List
from jira import JIRA
from auto_documentation.ticket_ingestion.configs.jira_config import JiraConfig
from auto_documentation.ticket_ingestion.configs.ticket_tree import TicketTree
from collections import deque

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

    def get_parent_ticket(self, ticket_tree: TicketTree):
        jql_query = f'project="{self.jira_config.project_name}" AND summary~"{ticket_tree.ticket_name}" AND issuetype="{ticket_tree.ticket_type}"'
        return jql_query

    def get_issue_links(self, issue_key: str) -> str:
        url = f"{self.jira_config.project_url}/rest/api/3/issue/{issue_key}?expand=issuelinks,issuelinks.outwardIssue.fields.issuetype"
        return url

    def get_issues(self):
        parent_issue_query = self.get_parent_ticket(self.ticket_tree)

    
    def build_formatted_tree(self) -> None:
        initial_parent: List[Dict] = {}
        queue = deque((initial_parent, ))

        while queue:
            next_issue = queue.pop()
            next_issue_field = next_issue["fields"]
            summary = next_issue_field["summary"]
            description = next_issue_field["description"]
            # Build markdown from summary and description
            for_markdown = [summary, description]
            self.formatted_tree[next_issue["key"]] = for_markdown

            for issue in next_issue_field["issueLinks"]:
                if "outwardIssue" in issue:
                    # Add issue to queue -> after checking it is in the correct sequence in TicketTree
                    ...


        

