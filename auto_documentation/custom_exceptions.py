class PromptBuilderError(Exception):
    """Base exception for PromptBuilder errors."""

    def __init__(self, message: str, ticket_id: str = None):
        self.ticket_id = ticket_id
        if ticket_id:
            super().__init__(f"{message} Ticket ID: {ticket_id}")
        else:
            super().__init__(message)


class InvalidTicketStructureError(PromptBuilderError):
    """Raised when the ticket structure is invalid."""

    def __init__(self, message: str, ticket_id: str = None):
        self.ticket_id = ticket_id
        if ticket_id:
            super().__init__(f"{message} Ticket ID: {ticket_id}")
        else:
            super().__init__(message)


class CyclicTicketRelationshipError(PromptBuilderError):
    """Raised when a cyclic relationship is detected in the ticket tree."""

    def __init__(self, message: str, ticket_id: str = None):
        self.ticket_id = ticket_id
        if ticket_id:
            super().__init__(f"{message} Ticket ID: {ticket_id}")
        else:
            super().__init__(message)
