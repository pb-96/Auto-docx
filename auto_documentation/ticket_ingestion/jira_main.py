from typing import Dict, Any, List, Union, Set, cast
from jira import JIRA
from auto_documentation.ticket_ingestion.configs.jira_config import JiraConfig
from auto_documentation.ticket_ingestion.configs.ticket_tree import TicketTree
from collections import deque
from functools import lru_cache


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

    def get_issues(self) -> str:
        parent_issue_query = self.get_parent_ticket(self.ticket_tree)
        return parent_issue_query

    def find_node_in_ticket_tree(self, ticket_name: str) -> Union[TicketTree, None]:
        if self.ticket_tree.ticket_name == ticket_name:
            return self.ticket_tree

        search = deque(self.ticket_tree.child)
        while search:
            next_search = search.pop()
            if next_search.ticket_name == ticket_name:
                return next_search
            for child in next_search.child:
                if child.ticket_name == ticket_name:
                    return child
                else:
                    search.append(child)

    @lru_cache
    def get_next_children_set(self, current_node: TicketTree) -> Set[str]:
        return {child.ticket_type for child in current_node.child}

    def add_child_to_queue(
        self, next_issue_field: Dict, current_node: TicketTree, queue: deque
    ):
        issue: Dict
        for issue in next_issue_field.get("issueLinks") or []:
            outward_issue = issue.get("outwardIssue")
            if outward_issue is not None:
                continue
                # Add issue to queue -> after checking it is in the correct sequence in TicketTree
            outward_issue: Dict = issue["outward_issue"]
            fields = outward_issue.get("fields")
            if fields is None:
                continue
            summary = outward_issue.get("summary")
            if summary is None:
                continue
            issue_type = outward_issue.get("issueType")
            if issue_type is None:
                continue
            if issue_type in current_node:
                queue.append(outward_issue["key"])

    def build_formatted_tree(self) -> None:
        initial_parent_query: str = self.get_parent_ticket(self.ticket_tree)
        queue: deque = deque((initial_parent_query,))

        while queue:
            url_to_query = queue.pop()
            print(url_to_query)
            next_issue = {}
            next_issue_field: Dict = next_issue.get("fields")
            if next_issue_field is None:
                continue
            summary = next_issue_field.get("summary")
            description = next_issue_field.get("description")
            issue_type_dict = next_issue_field.get("issueType")
            if issue_type_dict is None:
                continue
            issue_type = cast(dict, issue_type_dict).get("name")
            if issue_type is None:
                continue
            # Build markdown from summary and description
            current_node = self.find_node_in_ticket_tree(issue_type)
            for_markdown = [summary, description]
            self.formatted_tree[next_issue["key"]] = {
                "markdown": for_markdown,
                "parent": (
                    current_node.parent.ticket_name
                    if current_node.parent is not None
                    else None
                ),
                "ticket_type": current_node.ticket_type,
                "children": [],
            }

            self.add_child_to_queue(next_issue_field, current_node, queue)
