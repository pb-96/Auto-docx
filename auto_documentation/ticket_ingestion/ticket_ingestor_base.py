from typing import Dict, Any, List, Union, Set, cast
from auto_documentation.ticket_ingestion.configs.jira_config import JiraConfig
from auto_documentation.ticket_tree.ticket_tree import TicketTree
from collections import deque, defaultdict

ERROR_MESSAGE = "Subclasses must implement this method"


class GenericIngester:

    def __init__(
        self, jira_config: JiraConfig, ticket_tree: TicketTree, parent_ticket_id: str
    ):
        self.jira_config = jira_config
        self.ticket_tree = ticket_tree
        self.parent_ticket_id = parent_ticket_id
        self.formatted_tree: Dict[str, Any] = {}
        self._node_cache = {}
        self.types_to_keys = defaultdict(list)
        self.build_formatted_tree()

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

    def link_to_parent(self, current_node: TicketTree, key_to_query: str):
        if current_node.parent is None:
            return

        mapped = self.types_to_keys.get(current_node.parent.ticket_type)
        for key in mapped:
            associated = self.formatted_tree.get(key)
            associated["children"].append(key_to_query)

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

    def build_formatted_tree(self) -> None:
        raise NotImplementedError(ERROR_MESSAGE)

    def append_next(self, current_node: TicketTree, queue: deque, next_issue: Any):
        raise NotImplementedError(ERROR_MESSAGE)

    def build_entry(self, next_issue: Any, current_node: TicketTree):
        raise NotImplementedError(ERROR_MESSAGE)

    def _is_valid_issue_link(self, issue_link: Any) -> Union[Dict, None]:
        raise NotImplementedError(ERROR_MESSAGE)

    def get_issue_data(self, issue_key: str):
        raise NotImplementedError(ERROR_MESSAGE)
