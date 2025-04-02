from pydantic import BaseModel
from typing import List, Union, Literal
from enum import Enum


class ActionType(str, Enum):
    DESCRIPTION = "Description"
    TEST = "Test"


class JiraConfig(BaseModel):
    # Would need to store the passwords correctly
    email: str
    auth: str


class TicketTree(BaseModel):
    # Basically this the model that maps from the parent ticket to the test
    parent: Union["TicketTree", None]
    ticket_name: str
    ticket_type: str
    child: List["TicketTree"] = []
    action: ActionType = ActionType.DESCRIPTION

    def __init__(self, **data):
        super().__init__(**data)

    def relationship_pointer(self, string: str, indent: int = 0):
        left = "-" * indent
        return f"{left}>{string}\n"

    def display_relationship(self):
        initial_index = 0
        result_str = self.relationship_pointer(self.ticket_type, initial_index)
        # BFS style display
        for _child in self.child:
            initial_index = 2
            result_str += self.relationship_pointer(
                _child.ticket_type, indent=initial_index
            )
            next_children = _child.child
            if len(next_children):
                initial_index = initial_index + 2
                while next_children:
                    next_child = next_children.pop()
                    result_str += self.relationship_pointer(
                        next_child.ticket_type, indent=initial_index + 2
                    )
                    next_children.extend(next_child.child)
                    initial_index += 2
        return result_str

    def __repr__(self):
        return self.display_relationship()


JIRA_INSTANCE = TicketTree(
    **{
        "parent": None,
        "ticket_name": "Up Coming Release",
        "ticket_type": "Epic",
    }
)

FeatureDescription = TicketTree(
    **{
        "parent": JIRA_INSTANCE,
        "ticket_name": "Users can log in",
        "ticket_type": "FeatureDescription",
    }
)


NonFunctionalRequirements = TicketTree(
    **{
        "parent": FeatureDescription,
        "ticket_name": "Users must enter complex password",
        "ticket_type": "FeatureDescription",
    }
)

FunctionalRequirements = TicketTree(
    **{
        "parent": FeatureDescription,
        "ticket_name": "Must check users enter complex password containing at least one number, special char and have 16 chars in total length",
        "ticket_type": "FeatureDescription",
    }
)

JIRA_INSTANCE.child.append(FeatureDescription)
FeatureDescription.child.append(NonFunctionalRequirements)
NonFunctionalRequirements.child.append(FunctionalRequirements)
