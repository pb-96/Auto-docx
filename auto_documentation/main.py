import argparse
import logging
from typing import Union
from pathlib import Path
from auto_documentation.custom_types import RunType, FileType, TicketSource, TicketTree
import yaml
from auto_documentation.utils import yaml_file_to_ticket_tree

logger = logging.getLogger(__name__)


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


def run(run_type: RunType, ticket_src: TicketSource, ticket_tree_src: FileType): ...


def init_args():
    parser = argparse.ArgumentParser()
    # This would ether be build docs or
    parser.add_argument("--run_type", required=True)
    parser.add_argument("--ticket-source", required=True)
    parser.add_argument("--ticket-tree-src", required=True)
    args = parser.parse_args()
    # Could throw an error here need to handle
    run_type = RunType(args.run_type)
    ticket_src = TicketSource(args.ticket_source)
    return {
        "run_type": run_type,
        "ticket_src": ticket_src,
        "ticket_tree_src": args.ticket_tree_src,
    }


if __name__ == "__main__":
    args = init_args()
    run(**args)
