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
        self._node_cache = {}

    def get_issue_data(self, issue_key: str):
        return self.jira.issue(issue_key).fields

    def find_node_in_ticket_tree(self, ticket_type: str) -> Union[TicketTree, None]:
        if ticket_type in self._node_cache:
            return self._node_cache[ticket_type]

        if self.ticket_tree.ticket_type == ticket_type:
            self._node_cache[ticket_type] = self.ticket_tree
            return self.ticket_tree

        search = deque(self.ticket_tree.child)
        while search:
            next_search = search.pop()
            if next_search.ticket_type == ticket_type:
                return next_search
            for child in next_search.child:
                if child.ticket_type == ticket_type:
                    self._node_cache[ticket_type] = child
                    return child
                else:
                    search.append(child)

        return None

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
            if target_key is None:
                continue
            ticket_name = target_key["fields"]["issuetype"]["name"]
            key = target_key.get("key")
            if key and ticket_name and ticket_name in next_children:
                next_associated_issues.append(key)

        queue.extend(next_associated_issues)

    def link_to_parent(self, current_node: TicketTree, key_to_query: str):
        if current_node.parent is None:
            return

        associated = self.formatted_tree.get(key_to_query) or {}
        if not associated:
            return
        associated_parent = associated.get("parent") or {}
        if not associated_parent:
            return
        associated_children = associated_parent.get("children")
        if associated_children is None:
            return
        associated_children = cast(list, associated_children)
        for child_link in current_node.child:
            associated_children.append(child_link.ticket_type)

    def build_entry(self, next_issue: Any, current_node: TicketTree):
        return {
            "markdown": [next_issue.summary, next_issue.description],
            "parent": (
                current_node.parent.ticket_type
                if current_node.parent is not None
                else None
            ),
            "ticket_type": current_node.ticket_type,
            "children": [],
        }

    def build_formatted_tree(self) -> None:
        queue: deque = deque((self.parent_ticket_id,))
        while queue:
            key_to_query = queue.pop()
            next_issue = self.get_issue_data(key_to_query)
            current_node = self.find_node_in_ticket_tree(str(next_issue.issuetype))
            self.formatted_tree[key_to_query] = self.build_entry(
                next_issue, current_node
            )
            self.link_to_parent(current_node, key_to_query)
            self.append_next(current_node, queue, next_issue)

    def get_ticket_tree_as_markdown(self):
        # Have to maintain the tree order
        markdown = ""
        parent = {k: v for k, v in self.formatted_tree.items() if v["parent"] is None}
        if len(parent) > 1:
            raise ValueError("Only one parent ticket can exist")

        summary, content = parent["markdown"]
        summary = f"# {summary}\n"
        markdown += summary
        markdown += content
        markdown += "\n"

        return markdown
