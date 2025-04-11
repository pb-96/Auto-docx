

class PromptBuilderError(Exception):
    """Base exception for PromptBuilder errors."""

    pass


class InvalidTicketStructureError(PromptBuilderError):
    """Raised when the ticket structure is invalid."""

    pass