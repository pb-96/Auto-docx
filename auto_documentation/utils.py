from auto_documentation.ticket_ingestion.configs.ticket_tree import TicketTree
from typing import Generator


def ticket_tree_is_testable(ticket_tree: TicketTree) -> bool:
    return ticket_tree.action is not None and ticket_tree.action == "Test"


def find_testable_ticket(ticket_tree: TicketTree) -> Generator[TicketTree, None, None]:
    if ticket_tree_is_testable(ticket_tree):
        yield ticket_tree
    for child in ticket_tree.child:
        if ticket_tree_is_testable(child):
            yield child
        else:
            yield from find_testable_ticket(child)
