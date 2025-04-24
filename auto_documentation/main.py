import argparse
import logging
from typing import Union
from auto_documentation.custom_exceptions import InvalidTicketStructureError
from auto_documentation.custom_types import RunType, FileType, TicketSource
from auto_documentation.ticket_ingestion.jira_main import IngestJira
from auto_documentation.utils import (
    get_ticket_tree_structure,
    write_prompt_to_file,
    find_testable_ticket,
)
from dynaconf import Dynaconf
from auto_documentation.prompt_builder.prompt_builder import PromptBuilder
from auto_documentation.test_runner.test_runner import TestRunner
from auto_documentation.convert_to_file.to_pdf import HtmlToPdfConverter
from auto_documentation.convert_to_file.to_word import HtmlToWordConverter
from auto_documentation.markdown_converter.markdown import parse as md_parse
from auto_documentation.markdown_converter.html_validator import HTMLProcessor

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
    ticket_tree_src: Union[FileType, None],
    parent_ticket_id: str,
    output_file_path: Union[str, None],
    document_type: Union[str, None],
    test_folder: Union[str, None],
):
    if ticket_tree_src is not None:
        try:
            loaded_ticket_tree = get_ticket_tree_structure(
                ticket_tree_src=ticket_tree_src
            )
        except InvalidTicketStructureError as e:
            raise InvalidTicketStructureError(
                "Invalid ticket structure found in the ticket tree src file",
                e,
            )
    else:
        loaded_ticket_tree = None

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
            ticket_src_cls.build_formatted_tree()
            prompts = PromptBuilder(
                ticket_ingester=ticket_src_cls,
                output_path=output_file_path,
            ).build_prompt()
            write_prompt_to_file(prompts, output_file_path)
        case RunType.BUILD_TREE:
            ticket_src_cls.build_tree_from_ticket_id(output_file_path)
        case RunType.GEN_DOCS:
            # First run tests -> then build the docs
            ticket_src_cls.build_formatted_tree()
            testable_keys = find_testable_ticket(ticket_src_cls)
            test_runner = TestRunner(
                src_folder=test_folder,
                testable_keys=testable_keys,
            )
            test_runner.run_tests()
            if document_type is None:
                raise ValueError("Document type is required")

            md = ticket_src_cls.get_ticket_tree_as_markdown()
            as_html_tree = md_parse(md)
            valid_html = HTMLProcessor(as_html_tree)

            match document_type:
                case "pdf":
                    HtmlToPdfConverter(
                        html_node=valid_html, test_output_path=output_file_path
                    )
                case "word":
                    HtmlToWordConverter(
                        html_node=valid_html.root, test_output_path=output_file_path
                    )
                case _:
                    raise ValueError("Unsupported document type")


def init_args():
    parser = argparse.ArgumentParser()
    # This would ether be build docs or
    parser.add_argument("--run-type", required=True)
    parser.add_argument("--ticket-source", required=True)
    parser.add_argument("--ticket-tree-src", required=True)
    parser.add_argument("--parent-ticket-id", required=True)
    parser.add_argument("--output-file-path", required=False)
    parser.add_argument("--document-type", required=False)
    parser.add_argument("--test-folder", required=False)
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
        "document_type": args.document_type,
        "test_folder": args.test_folder,
    }


if __name__ == "__main__":
    args = init_args()
    run(**args)
