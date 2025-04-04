from pydantic import BaseModel
from auto_documentation.ticket_ingestion.configs.ticket_tree import TicketTree


class JiraConfig(BaseModel):
    # Would need to store the passwords correctly
    email: str
    auth: str
    project_name: str
    project_url: str


JIRA_INSTANCE = TicketTree(
    **{
        "parent": None,
        "ticket_name": "Up Coming Release",
        "ticket_type": "Epic",
    }
)

Requirement = TicketTree(
    **{
        "parent": JIRA_INSTANCE,
        "ticket_name": "Up Coming Requirement",
        "ticket_type": "Requirement",
    }
)

NonFunctionalRequirements = TicketTree(
    **{
        "parent": Requirement,
        "ticket_name": "Users must enter complex password",
        "ticket_type": "NonFunctionalReq",
    }
)

FunctionalRequirements = TicketTree(
    **{
        "parent": NonFunctionalRequirements,
        "ticket_name": "Must check users enter complex password containing at least one number, special char and have 16 chars in total length",
        "ticket_type": "FunctionalReq",
        "action": "Test",
    }
)

JIRA_INSTANCE.child.append(Requirement)
Requirement.child.append(NonFunctionalRequirements)
NonFunctionalRequirements.child.append(FunctionalRequirements)
