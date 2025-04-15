import argparse
import logging
from typing import Union
from auto_documentation.custom_exceptions import InvalidTicketStructureError
from auto_documentation.custom_types import RunType, FileType, TicketSource
from auto_documentation.ticket_ingestion.jira_main import IngestJira
from auto_documentation.utils import get_ticket_tree_structure, write_prompt_to_file
from dynaconf import Dynaconf
from auto_documentation.prompt_builder.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


# Initialize Dynaconf
settings = Dynaconf(
    envvar_prefix="MD_PARSER",
    settings_files=[
        "settings.yaml",
        "auto_documentation/secrets.toml",
    ],
    environments=True,
    load_dotenv=True,
)


def run(
    run_type: RunType,
    ticket_src: TicketSource,
    ticket_tree_src: FileType,
    parent_ticket_id: str,
    output_file_path: Union[str, None],
):

    try:
        loaded_ticket_tree = get_ticket_tree_structure(ticket_tree_src=ticket_tree_src)
    except InvalidTicketStructureError as e:
        raise InvalidTicketStructureError(
            "Invalid ticket structure found in the ticket tree src file",
            e,
        )

    match ticket_src:
        case TicketSource.JIRA:
            # Also just initialize the class here
            ticket_src_cls = IngestJira(
                jira_config=settings,
                ticket_tree=loaded_ticket_tree,
                parent_ticket_id=parent_ticket_id,
            )
        case _:
            raise ValueError("Unsupported Ticket src command given")

    match run_type:
        case RunType.TEST_CREATE:
            prompts = PromptBuilder(
                ticket_ingester=ticket_src_cls,
                output_file_path=output_file_path,
            ).build_prompt()
            write_prompt_to_file(prompts, output_file_path)
        case RunType.BUILD_TREE:
            # Write the ticket tree to yaml
            ticket_tree = ticket_src_cls.build_tree_from_ticket_id(parent_ticket_id)
            # Would need to write the ticket tree to yaml
        case RunType.GEN_DOCS:
            pass


def init_args():
    parser = argparse.ArgumentParser()
    # This would ether be build docs or
    parser.add_argument("--run-type", required=True)
    parser.add_argument("--ticket-source", required=True)
    parser.add_argument("--ticket-tree-src", required=True)
    parser.add_argument("--parent-ticket-id", required=True)
    parser.add_argument("--output-file-path", required=False)
    args = parser.parse_args()
    # Could throw an error here need to handle

    run_type = RunType(args.run_type)
    ticket_src = TicketSource(args.ticket_source)

    return {
        "run_type": run_type,
        "ticket_src": ticket_src,
        "ticket_tree_src": args.ticket_tree_src,
        "parent_ticket_id": args.parent_ticket_id,
        "output_file_path": args.output_file_path,
    }


if __name__ == "__main__":
    args = init_args()
    run(**args)
