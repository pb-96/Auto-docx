from typing import Dict, Any, List, Union, Set, cast
from jira import JIRA
from auto_documentation.ticket_ingestion.configs.jira_config import (
    JiraConfig,
    JIRA_INSTANCE,
)
from auto_documentation.ticket_ingestion.configs.ticket_tree import TicketTree
from collections import deque
from functools import lru_cache
from collections import defaultdict
from auto_documentation.ticket_ingestion.ticket_ingestor_base import GenericIngester

class IngestJira(GenericIngester):
    def __init__(
        self, jira_config: JiraConfig, ticket_tree: TicketTree, parent_ticket_id: str
    ):
        self.jira = JIRA(
            server=self.jira_config.project_url,
            basic_auth=(self.jira_config.email, self.jira_config.auth),
        )
        self.project = self.jira.project(jira_config.project_name)
        super().__init__(jira_config, ticket_tree, parent_ticket_id)

    def get_issue_data(self, issue_key: str):
        return self.jira.issue(issue_key).fields

    def _is_valid_issue_link(self, issue_link: Any) -> Union[Dict, None]:

        if not hasattr(issue_link, "raw"):
            return None

        fields = issue_link.raw or {}
        if "inwardIssue" in fields:
            return fields.get("inwardIssue") or {}
        elif "outwardIssue" in fields:
            return fields.get("outwardIssue") or {}
        else:
            return None

    def append_next(self, current_node: TicketTree, queue: deque, next_issue):
        next_children = self.get_next_children_set(current_node)
        if not next_children:
            return

        next_associated_issues = []
        for issue_link in next_issue.issuelinks:
            target_key = self._is_valid_issue_link(issue_link)
            if target_key is None:
                continue
            ticket_name = target_key["fields"]["issuetype"]["name"]
            key = target_key.get("key")
            if key and ticket_name and ticket_name in next_children:
                next_associated_issues.append(key)

        queue.extend(next_associated_issues)

    def build_entry(self, next_issue: Any, current_node: TicketTree):
        return {
            "markdown": [next_issue.summary, next_issue.description],
            "parent": (
                current_node.parent.ticket_type if current_node.parent else None
            ),
            "ticket_type": current_node.ticket_type,
            "children": [],
        }

    def build_formatted_tree(self) -> None:
        queue: deque = deque((self.parent_ticket_id,))
        while queue:
            key_to_query = queue.pop()
            next_issue = self.get_issue_data(key_to_query)
            string_issue_type = str(next_issue.issuetype)
            self.types_to_keys[string_issue_type].append(key_to_query)
            current_node = self.find_node_in_ticket_tree(string_issue_type)
            self.formatted_tree[key_to_query] = self.build_entry(
                next_issue, current_node
            )
            self.link_to_parent(current_node, key_to_query)
            self.append_next(current_node, queue, next_issue)

