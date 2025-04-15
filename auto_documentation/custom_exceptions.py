class PromptBuilderError(Exception):
    """Base exception for PromptBuilder errors."""



class InvalidTicketStructureError(PromptBuilderError):
    """Raised when the ticket structure is invalid."""

