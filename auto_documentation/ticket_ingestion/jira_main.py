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


class IngestJira:
    def __init__(
        self, jira_config: JiraConfig, ticket_tree: TicketTree, parent_ticket_id: str
    ):
        self.jira_config = jira_config
        self.ticket_tree = ticket_tree
        self.formatted_tree: Dict[str, Any] = {}
        self.jira = JIRA(
            server=self.jira_config.project_url,
            basic_auth=(self.jira_config.email, self.jira_config.auth),
        )
        self.project = self.jira.project(jira_config.project_name)
        self.parent_ticket_id = parent_ticket_id
        self.ticket_type_to_keys = defaultdict(list)

    def get_issue_data(self, issue_key: str):
        return self.jira.issue(issue_key).fields

    @lru_cache
    def find_node_in_ticket_tree(self, ticket_type: str) -> Union[TicketTree, None]:
        if self.ticket_tree.ticket_type == ticket_type:
            return self.ticket_tree

        search = deque(self.ticket_tree.child)
        while search:
            next_search = search.pop()
            if next_search.ticket_type == ticket_type:
                return next_search
            for child in next_search.child:
                if child.ticket_type == ticket_type:
                    return child
                else:
                    search.append(child)

    def get_next_children_set(self, current_node: TicketTree) -> Set[str]:
        return {child.ticket_type for child in current_node.child}

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
            ticket_name = target_key["fields"]["issuetype"]["name"]
            key = target_key.get("key")
            if key and ticket_name and ticket_name in next_children:
                next_associated_issues.append(key)

        queue.extend(next_associated_issues)

    def link_to_parent(self, current_node: TicketTree, key_to_query: str):
        self.ticket_type_to_keys[current_node.ticket_type].append(key_to_query)
        if current_node.parent is None:
            return

        for child_link in self.ticket_type_to_keys[current_node.ticket_type]:
            associated = self.formatted_tree.get(child_link) or {}
            if not associated:
                continue
            associated_children = associated.get("children")
            if associated_children is None:
                continue
            associated_children.append(child_link)

    def build_formatted_tree(self) -> None:
        queue: deque = deque((self.parent_ticket_id,))
        while queue:
            key_to_query = queue.pop()
            next_issue = self.get_issue_data(key_to_query)
            summary = next_issue.summary
            description = next_issue.description
            issue_type = next_issue.issuetype
            current_node = self.find_node_in_ticket_tree(str(issue_type))
            for_markdown = [summary, description]
            self.formatted_tree[key_to_query] = {
                "markdown": for_markdown,
                "parent": (
                    current_node.parent.ticket_type
                    if current_node.parent is not None
                    else None
                ),
                "ticket_type": current_node.ticket_type,
                "children": [],
            }

            self.link_to_parent(current_node, key_to_query)
            self.append_next(current_node, queue, next_issue)
