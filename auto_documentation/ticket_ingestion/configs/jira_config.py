from pydantic import BaseModel
from auto_documentation.ticket_ingestion.configs.ticket_tree import TicketTree
from typing import TypedDict, Union, List


class TicketDict(TypedDict):
    title: str
    description: str
    parent_type: Union[str, None]
    parent_key: Union[str, None]
    ticket_type: str
    children: List[str]


class JiraConfig(BaseModel):
    # Would need to store the passwords correctly
    email: str
    auth: str
    project_name: str
    project_url: str


JIRA_INSTANCE = TicketTree(
    **{
        "parent": None,
        "ticket_type": "Epic",
    }
)

Requirement = TicketTree(
    **{
        "parent": JIRA_INSTANCE,
        "ticket_type": "Requirement",
    }
)

NonFunctionalRequirements = TicketTree(
    **{
        "parent": Requirement,
        "ticket_type": "NonFunctionalReq",
    }
)

FunctionalRequirements = TicketTree(
    **{
        "parent": NonFunctionalRequirements,
        "ticket_type": "FunctionalReq",
        "action": "Test",
    }
)

JIRA_INSTANCE.child.append(Requirement)
Requirement.child.append(NonFunctionalRequirements)
NonFunctionalRequirements.child.append(FunctionalRequirements)
