from auto_documentation.custom_types import TicketTree


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
