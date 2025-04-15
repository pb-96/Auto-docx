from auto_documentation.custom_types import TicketTree, FileType
from typing import Generator, Dict, Any
import jsonlines
import yaml
from pathlib import Path


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


def get_ticket_tree_structure(ticket_tree_src: FileType) -> TicketTree:
    if ticket_tree_src is None:
        raise ValueError("Please add valid path to ticket tree config")
    # Check if string is a valid path
    if isinstance(ticket_tree_src, str):
        ticket_tree_src = Path(ticket_tree_src)

    try:
        with open(ticket_tree_src, mode="r") as src:
            yaml_data = yaml.safe_load(src)
    except yaml.YAMLError as exc:
        raise yaml.YAMLError("Could not open src file")

    # Parse yaml file to ticket tree
    as_ticket_tree = yaml_file_to_ticket_tree(yaml_dict=yaml_data)
    return as_ticket_tree


def yaml_file_to_ticket_tree(yaml_dict: Dict[str, Any]) -> TicketTree:
    root: Dict[str, Any] = yaml_dict["root"]
    children = root.pop("child")
    as_ticket_tree = TicketTree(**root)
    parent = as_ticket_tree

    while children:
        if "child" in children:
            next_children = children.pop("child")
            # TODO: Here is where we need to handle the case where the children is a list
            # For now we assume only one child is allowed
            # Here is where we need to handle the case where the children is a list
            assert isinstance(next_children, dict)
        else:
            next_children = None
        children["parent"] = parent
        as_ticket = TicketTree(**children)
        parent.child.append(as_ticket)
        parent = as_ticket
        children = next_children

    return as_ticket_tree
