from pydantic import BaseModel


class JiraConfig(BaseModel):
    # Would need to store the passwords correctly
    email: str
    auth: str


class JiraTree(BaseModel):
    # Basically this the model that maps from the parent ticket to the test
    parent: str
    ticket_name: str
    child: "JiraTree"