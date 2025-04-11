from typing import TypedDict, Optional, Dict, Any
from pydantic import BaseModel
from typing import List, Union, Literal
from enum import Enum


# Constants
SEPARATOR = f'{"*" * 100}\n'

# Type definitions
TicketKey = str
TicketType = str
TicketDescription = Dict[str, str]
TicketDescriptions = Dict[TicketKey, TicketDescription]
PromptDict = Dict[str, Any]

class TicketMetadata(TypedDict):
    title: str
    description: str
    ticket_type: str
    parent_key: Optional[str] = None


class ActionType(str, Enum):
    DESCRIPTION = "Description"
    TEST = "Test"


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



class TestBuilderPrompt(TypedDict):
    tree_structure: str
    parent_ticket_type: str
    child_ticket_type: str
    ticket_descriptions: str
    python_version: str
    test_name: str



class TicketTree(BaseModel):
    # Basically this the model that maps from the parent ticket to the test
    parent: Union["TicketTree", None]
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
