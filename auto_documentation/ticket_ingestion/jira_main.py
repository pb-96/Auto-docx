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
        self.types_to_keys = defaultdict(list)

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

        mapped = self.types_to_keys.get(current_node.parent.ticket_type)
        for key in mapped:
            associated = self.formatted_tree.get(key)
            associated["children"].append(key_to_query)

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

    def parse_markdown(self, formated_entry: Dict[str, Any], heading_level: int = 1):
        """Parse a formatted entry into markdown with appropriate heading level."""
        title, summary = formated_entry["markdown"]
        heading_prefix = "#" * heading_level
        title = f"{heading_prefix} {title}\n"
        summary = f"{summary}\n\n"
        return title + summary

    def get_ticket_tree_as_markdown(self) -> str:
        """Generate markdown representation of the ticket tree using DFS traversal."""
        # Find the parent ticket
        parent_keys = self.types_to_keys.get(self.ticket_tree.ticket_type, [])

        if not parent_keys:
            raise ValueError(
                f"No parent ticket found of type {self.ticket_tree.ticket_type}"
            )
        if len(parent_keys) > 1:
            raise ValueError(f"Multiple parent tickets found: {parent_keys}")

        parent_ticket = self.formatted_tree.get(parent_keys[0])
        if not parent_ticket:
            raise ValueError(
                f"Parent ticket {parent_keys[0]} not found in formatted tree"
            )

        markdown = self.parse_markdown(parent_ticket, heading_level=1)
        markdown += self.process_children(parent_keys[0], heading_level=2)

        return markdown

    def process_children(self, parent_key: str, heading_level: int) -> str:
        result = ""
        parent_entry = self.formatted_tree.get(parent_key)
        if not parent_entry:
            return result
        children = parent_entry.get("children", [])
        for child_key in children:
            child_entry = self.formatted_tree.get(child_key)
            if not child_entry:
                continue
            result += self.parse_markdown(child_entry, heading_level)
            result += self.process_children(child_key, heading_level + 1)
        return result

