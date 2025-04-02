from typing import Dict
from jira import JIRA
from auto_documentation.ticket_ingestion.configs.jira_config import JiraConfig


class IngestJita:
    def __init__(self, jira_config: JiraConfig):
        self.jira_config = jira_config
        self.jira_object = JIRA()

    def perform_auth(self):
        email, auth = self.jira_config.email, self.jira_config.auth

    def get_jira_issues(self): ...
