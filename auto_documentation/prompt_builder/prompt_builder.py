from auto_documentation.ticket_ingestion.ticket_ingestor_base import GenericIngester
from auto_documentation.utils import (
    find_testable_ticket,
    is_leaf,
)
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
from typing import Dict, List, Tuple, Any, Generator
import logging

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    This class takes ticket information from various sources and constructs
    prompts that can be used to generate tests.
    """

    def __init__(
        self,
        ticket_ingester: GenericIngester,
        output_path: str,
    ):
        self.prompt: Dict[str, Any] = {}
        self.ticket_ingester = ticket_ingester
        self.output_path = output_path
        self.prompts = self.build_prompt()

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
                    f"{'This is what the test you write is based on' if is_tester else ''}\n",
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
            "src_folder": self.output_path,
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
            ticket_description = self.build_prompt_string(
                upward_order, child_key, ticket_descriptions
            )
            # This allows the user to use the default prompt or the custom prompt from the output given
            prompt_meta = self.build_prompt_dict(
                ticket_descriptions=ticket_description,
                ticket_tree_structure=ticket_tree_structure,
                parent_ticket_type=parent_key,
                ticket_type=ticket_type,
                child_key=child_key,
            )
            # prompt = test_builder_prompt(prompt_meta)
            return {
                child_key: {
                    "prompt_meta": prompt_meta,
                    # "prompt": prompt,
                }
            }

        except Exception as e:
            logger.error(f"Error processing ticket {child_key}: {e}")

    def build_prompt(self) -> Generator[Tuple[TicketKey, str], None, None]:
        try:
            testable_target = [*find_testable_ticket(self.ticket_ingester.ticket_tree)]
            if (
                not all((is_leaf(ticket) for ticket in testable_target))
                or not testable_target
            ):
                raise InvalidTicketStructureError("Testable target is not a leaf")

            ticket_tree_structure = (
                self.ticket_ingester.ticket_tree.display_relationship()
            )
            parent_ticket_type = self.ticket_ingester.ticket_tree.ticket_type

            if parent_ticket_type not in self.ticket_ingester.types_to_keys:
                raise InvalidTicketStructureError(
                    f"Parent ticket type {parent_ticket_type} not found"
                )
            parent_keys = self.ticket_ingester.types_to_keys[parent_ticket_type]
            assert len(parent_keys) == 1, (
                f"Expected exactly one parent key, got {len(parent_keys)}"
            )

            parent_key = next(iter(parent_keys))
            for ticket in testable_target:
                ticket_type = ticket.ticket_type
                for child_key in self.ticket_ingester.types_to_keys.get(
                    ticket_type, []
                ):
                    prompt = self.process_ticket(
                        child_key, parent_key, ticket_tree_structure, ticket_type
                    )
                    yield prompt

        except Exception as e:
            logger.error(f"Error building prompt: {e}")
            raise PromptBuilderError(f"Failed to build prompt: {e}")

    def __iter__(self):
        for prompt in self.prompts:
            yield prompt

    def __next__(self):
        return next(self.prompts)
