import logging
from typing import Union
from auto_documentation.custom_exceptions import InvalidTicketStructureError
from auto_documentation.custom_types import FileType
from auto_documentation.ticket_ingestion.jira_main import IngestJira
from auto_documentation.ticket_ingestion.ticket_ingestor_base import GenericIngester
from auto_documentation.utils import (
    get_ticket_tree_structure,
    find_testable_ticket,
)
from dynaconf import Dynaconf
from auto_documentation.test_runner.test_runner import TestRunner
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


def generate_html_for_docs(
    ticket_src_cls: GenericIngester, test_runner: TestRunner
) -> HTMLProcessor:
    ticket_src_cls.build_formatted_tree()
    testable_keys = find_testable_ticket(ticket_src_cls)
    test_runner.run_tests(testable_keys)
    md = ticket_src_cls.get_ticket_tree_as_markdown()
    as_html_tree = md_parse(md)
    valid_html = HTMLProcessor(as_html_tree)
    return valid_html


def run(
    ticket_tree_src: FileType,
    parent_ticket_id: str,
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
    ticket_src_cls = IngestJira(
        jira_config=settings,
        ticket_tree=loaded_ticket_tree,
        parent_ticket_id=parent_ticket_id,
    )

    generate_html_for_docs(ticket_src_cls, test_folder)
