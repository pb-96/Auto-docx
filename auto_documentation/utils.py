from auto_documentation.custom_types import TicketTree
from typing import Generator, Dict, Any
import jsonlines


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


def is_leaf(ticket_tree: TicketTree) -> bool:
    return len(ticket_tree.child) == 0 and ticket_tree_is_testable(ticket_tree)


# TODO: This would only work if each child has a depth of one -> would miss with multiple children
# Should adopt a bfs -> i.e search through all the children of the current node
def check_leaf_is_testable(ticket_tree: TicketTree) -> bool:
    if is_leaf(ticket_tree):
        return True

    for child in ticket_tree.child:
        if check_leaf_is_testable(child):
            return True
    return False


def write_to_jsonl(data: Dict[str, Any], file_path: str):
    with jsonlines.open(file_path, mode="w") as writer:
        writer.write(data)


def yaml_file_to_ticket_tree(yaml_dict: Dict[str, Any]) -> TicketTree:
    ...