from typing import Dict, Any, Union, List, Set
from jira import JIRA
from auto_documentation.custom_types import ActionType, TicketTree, TicketDict
from collections import deque
from auto_documentation.ticket_ingestion.ticket_ingestor_base import GenericIngester
from dynaconf import Dynaconf

class IngestJira(GenericIngester):
    def __init__(
        self,
        jira_config: Dynaconf,
        ticket_tree: Union[TicketTree, None],
        parent_ticket_id: str,
    ):
        self.jira = JIRA(
            server=jira_config.get("jira_project_url"),
            basic_auth=(jira_config.get("jira_email"), jira_config.get("jira_auth")),
        )
        self.project = self.jira.project(jira_config.get("jira_project_name"))
        super().__init__(jira_config, ticket_tree, parent_ticket_id)

    def get_issue_data(self, issue_key: str):
        return self.jira.issue(issue_key)

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

    def _process_issue_links(self, issue) -> List[str]:
        linked_keys = []
        for issue_link in issue.issuelinks:
            linked_issue = self._is_valid_issue_link(issue_link)
            if linked_issue is None:
                continue
            key = linked_issue.get("key")
            if key:
                linked_keys.append(key)
        return linked_keys

    def append_next(self, current_node: TicketTree, queue: deque, next_issue) -> None:
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

    def build_entry(
        self, next_issue: Any, current_node: TicketTree, last_key: Union[str, None]
    ) -> TicketDict:
        ticket_dict: TicketDict = {
            "title": next_issue.summary,
            "description": next_issue.description,
            "parent_type": (
                current_node.parent.ticket_type if current_node.parent else None
            ),
            "parent_key": last_key,
            "ticket_type": current_node.ticket_type,
            "children": [],
        }
        return ticket_dict

    def build_formatted_tree(self) -> None:
        if self.ticket_tree is None:
            raise ValueError("Ticket tree is None")

        queue: deque = deque((self.parent_ticket_id,))
        last_key = None
        while queue:
            key_to_query = queue.pop()
            next_issue = self.get_issue_data(key_to_query).fields
            string_issue_type = str(next_issue.issuetype)
            self.types_to_keys[string_issue_type].append(key_to_query)
            # This is where we need to handle the case where the ticket tree is None
            # This would mean we have to build the ticket tree from the ticket id
            current_node = self.find_node_in_ticket_tree(string_issue_type)
            self.formatted_tree[key_to_query] = self.build_entry(
                next_issue, current_node, last_key
            )
            self.append_next(current_node, queue, next_issue)
            last_key = key_to_query

    def build_tree_from_ticket_id(self) -> TicketTree:
        # Get parent issue and create root node
        parent_issue = self.get_issue_data(self.parent_ticket_id)
        parent_ticket_type = str(parent_issue.fields.issuetype)
        parent_node = self._create_ticket_tree_node(parent_ticket_type)
        seen_types = set([parent_ticket_type])
        seen_parents_ids = set([self.parent_ticket_id])
        children = self._process_issue_links(parent_issue.fields)
        seen_parents_ids.update(children)
        queue = deque(children)
        last_seen_type = parent_node

        while queue:
            next_key = queue.popleft()
            next_issue = self.get_issue_data(next_key)
            issue_type = str(next_issue.fields.issuetype)
            current_node = self._create_ticket_tree_node(issue_type, last_seen_type)
            last_seen_type.child.append(current_node)
            last_seen_type = current_node
            seen_types.add(issue_type)
            seen_parents_ids.add(next_key)

            has_children = False
            for linked_key in self._process_issue_links(next_issue.fields):
                linked_issue = self.get_issue_data(linked_key)
                linked_type = linked_issue.fields.issuetype.name
                if linked_key in seen_parents_ids or linked_type in seen_types:
                    continue
                has_children = True
                queue.append(linked_key)

            if not has_children:
                current_node.action = ActionType.TEST

        self.ticket_tree = parent_node
        return parent_node

