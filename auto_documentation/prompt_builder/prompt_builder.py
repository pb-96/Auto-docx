from auto_documentation.prompt_builder.prompts import build_test_builder_prompt
from auto_documentation.ticket_ingestion.ticket_ingestor_base import GenericIngester
from auto_documentation.custom_types import TicketTree
from auto_documentation.utils import find_testable_ticket, is_leaf
from auto_documentation.custom_types import (
    TicketKey,
    TicketDescriptions,
    PromptDict,
    SEPARATOR,
)
from auto_documentation.custom_exceptions import (
    PromptBuilderError,
    InvalidTicketStructureError,
)
from typing import cast, Dict, List, Tuple, Any, Generator, TypeVar, Optional
from dataclasses import dataclass
import logging
from dynaconf import Dynaconf

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Builds prompts for test generation based on ticket information.

    This class takes ticket information from various sources and constructs
    prompts that can be used to generate tests.
    """

    def __init__(
        self,
        parent_ticket_id: str,
        ticket_ingester: GenericIngester,
        generic_config: Dynaconf,
        output_file_path: str,
        return_default_prompt: bool = True,
    ):
        self.prompt: Dict[str, Any] = {}
        self.ticket_ingester = ticket_ingester
        self.output_file_path = output_file_path
        self.return_default_prompt = return_default_prompt

        # Validate inputs
        if not parent_ticket_id:
            raise PromptBuilderError("Parent ticket ID cannot be empty")
        if not output_file_path:
            raise PromptBuilderError("Output file path cannot be empty")

    def get_ticket_description(
        self, child_key: TicketKey, parent_key: TicketKey
    ) -> Tuple[TicketDescriptions, List[TicketKey]]:

        ticket_descriptions: TicketDescriptions = {}
        upward_order: List[TicketKey] = [child_key]
        lookup = child_key

        try:
            while lookup != parent_key:
                metadata = self.ticket_ingester.formatted_tree[lookup]
                ticket_descriptions[lookup] = {
                    "title": metadata["title"],
                    "description": metadata["description"],
                    "ticket_type": metadata["ticket_type"],
                }
                lookup = metadata["parent_key"]
                upward_order.append(lookup)

            parent_metadata = self.ticket_ingester.formatted_tree[parent_key]
            ticket_descriptions[parent_key] = {
                "title": parent_metadata["title"],
                "description": parent_metadata["description"],
                "ticket_type": parent_metadata["ticket_type"],
            }
            upward_order.append(parent_key)
            upward_order.reverse()
            return ticket_descriptions, upward_order

        except KeyError as e:
            raise InvalidTicketStructureError(f"Missing key in ticket metadata: {e}")
        except Exception as e:
            logger.error(f"Error getting ticket description: {e}")
            raise PromptBuilderError(f"Failed to get ticket description: {e}")

    def build_prompt_string(
        self,
        upward_order: List[TicketKey],
        child_key: TicketKey,
        ticket_descriptions: TicketDescriptions,
    ) -> str:
        prompt_parts = []

        for key in upward_order:
            is_tester = key == child_key
            meta = ticket_descriptions[key]

            prompt_parts.extend(
                [
                    SEPARATOR,
                    f"This is a {'testable ticket' if is_tester else 'parent'} of type {meta['ticket_type']}\n",
                    f'{"This is what the test you write is based on" if is_tester else ""}\n',
                    SEPARATOR,
                    f"This is the ticket name: {meta['title']}\n",
                    SEPARATOR,
                    meta["description"],
                    "\n",
                ]
            )

        return "\n".join(prompt_parts)

    def build_prompt_dict(
        self,
        ticket_descriptions: str,
        ticket_tree_structure: str,
        parent_ticket_type: str,
        ticket_type: str,
        child_key: str,
    ) -> PromptDict:
        p_dict: PromptDict = {
            "tree_structure": ticket_tree_structure,
            "parent_ticket_type": parent_ticket_type,
            "child_ticket_type": ticket_type,
            "ticket_descriptions": ticket_descriptions,
            "test_name": child_key,
            "python_version": "3.11",
        }
        return p_dict

    def process_ticket(
        self,
        child_key: str,
        parent_key: str,
        ticket_tree_structure: str,
        ticket_type: str,
    ) -> Generator:
        try:
            ticket_descriptions, upward_order = self.get_ticket_description(
                child_key, parent_key
            )
            prompt_string = self.build_prompt_string(
                upward_order, child_key, ticket_descriptions
            )
            if self.return_default_prompt:
                prompt_meta = self.build_prompt_dict(
                    ticket_descriptions=prompt_string,
                    ticket_tree_structure=ticket_tree_structure,
                    parent_ticket_type=parent_key,
                    ticket_type=ticket_type,
                    child_key=child_key,
                )
                yield child_key, build_test_builder_prompt(prompt_meta)
            else:
                # Return the ticket string and the ticket tree structure
                yield child_key, (prompt_string, ticket_tree_structure)

        except Exception as e:
            logger.error(f"Error processing ticket {child_key}: {e}")
            # Continue processing other tickets even if one fails

    def build_prompt(self) -> Generator[Tuple[TicketKey, str], None, None]:
        """
        Build prompts for all testable tickets.

        This method finds all testable tickets in the ticket tree, builds descriptions
        for each ticket and its parents, and generates prompts for test generation.

        Yields:
            Tuples containing:
            - The key of the testable ticket
            - The generated prompt string

        Raises:
            InvalidTicketStructureError: If the ticket structure is invalid
            PromptBuilderError: If there's an error building the prompt
        """
        try:
            testable_target = [*find_testable_ticket(self.ticket_tree)]
            if (
                not all((is_leaf(ticket) for ticket in testable_target))
                or not testable_target
            ):
                raise InvalidTicketStructureError("Testable target is not a leaf")

            ticket_tree_structure = self.ticket_tree.display_relationship()
            parent_ticket_type = self.ticket_tree.ticket_type

            if parent_ticket_type not in self.ticket_ingester.types_to_keys:
                raise InvalidTicketStructureError(
                    f"Parent ticket type {parent_ticket_type} not found"
                )
            parent_keys = self.ticket_ingester.types_to_keys[parent_ticket_type]
            assert (
                len(parent_keys) == 1
            ), f"Expected exactly one parent key, got {len(parent_keys)}"
            parent_key = next(iter(parent_keys))

            for ticket in testable_target:
                ticket_type = ticket.ticket_type
                for child_key in self.ticket_ingester.types_to_keys.get(
                    ticket_type, []
                ):
                    yield from self.process_ticket(
                        child_key, parent_key, ticket_tree_structure, ticket_type
                    )
                else:
                    logger.warning(f"No child keys found for ticket type {ticket_type}")

        except Exception as e:
            logger.error(f"Error building prompt: {e}")
            raise PromptBuilderError(f"Failed to build prompt: {e}")
