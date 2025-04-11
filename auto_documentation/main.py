import argparse
import logging
from typing import Union
from pathlib import Path
from auto_documentation.custom_types import RunType, FileType, TicketSource
from auto_documentation.ticket_ingestion.ticket_ingestor_base import GenericIngester
from auto_documentation.ticket_ingestion.jira_main import IngestJira
from auto_documentation.utils import get_ticket_tree_structure

logger = logging.getLogger(__name__)


def run(run_type: RunType, ticket_src: TicketSource, ticket_tree_src: FileType):
    loaded_ticket_tree = get_ticket_tree_structure(ticket_tree_src=ticket_tree_src)
    ticket_src_cls: Union[GenericIngester, None] = None

    match ticket_src:
        case TicketSource.JIRA:
            # Also just initialize the class here
            ticket_src = IngestJira

    if ticket_src_cls is None:
        raise ValueError("Unsupported Ticket src command given")


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
