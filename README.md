# Auto Documentation & Test Generator

## Overview
A sophisticated automation framework that generates documentation and tests from ticket management systems (currently Jira, with Notion support planned). The system features advanced ticket tree processing capabilities, converting ticket hierarchies into structured documentation and test prompts.

## Features

### Implemented ✅
- Automated ticket tree generation from:
  - Jira tickets (fully implemented)
  - Support for complex ticket hierarchies
  - Intelligent parent-child relationship detection
- Document Processing
  - Ticket tree to structured documentation
  - Custom node type generation
  - YAML configuration support
- LLM-powered prompt generation
  - Automatic conversion of tickets to test prompts
  - Intelligent prompt creation based on ticket context
  - Support for different action types (DESCRIPTION, TEST)
- Configuration Management
  - Dynaconf integration
  - Environment-based configuration
  - Secure secrets management

### In Progress 🚧
- Notion Integration
  - Ticket ingestion from Notion
  - Notion-specific tree building
- Documentation Generation
  - Automated doc creation from ticket trees
  - Documentation pipeline
- Test Runner
  - Test execution framework
  - Result collection and reporting

## How It Works
1. **Ticket Processing Pipeline**
   ```mermaid
   graph TD;
       A[Ticket Source]-->B{Ticket Type};
       B-->|Jira|C[Jira Ingester];
       B-->|Notion|D[Notion Ingester];
       C-->E[Tree Builder];
       D-->E;
       E-->F[Prompt Generator];
       F-->G[Documentation/Test Output];
   ```

2. **Ticket Tree System**
   - Custom tree structure for ticket representation:
     ```python
     class TicketTree:
         ticket_type: str
         parent: Optional[TicketTree]
         child: List[TicketTree]
         action: ActionType  # DESCRIPTION or TEST
     ```

3. **Input Sources**
   - Jira epics and associated tickets (implemented)
   - Notion documents (planned)
   - Supported formats:
     - YAML configuration
     - Direct ticket ID input

4. **Tree Processing**
   - Ticket Processing:
     - Builds hierarchical tree structure
     - Maintains parent-child relationships
     - Detects and prevents cycles
   - Tree Generation:
     - Creates structured representation
     - Maintains relationship hierarchy
     - Sets appropriate action types

## Technical Architecture
- **Ticket Processing Layer**
  - Jira API integration
  - Tree builder
  - Cycle detection
  - Action type assignment

- **Configuration Management**
  - Dynaconf integration
  - Environment variables
  - Secrets management

- **Prompt Generation**
  - LLM integration layer
  - Template system
  - Action type handling

## Getting Started

### Prerequisites
- Python 3.8+
- Poetry for dependency management
- Jira API access (for Jira integration)

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Configure your environment:
   ```bash
   cp auto_documentation/secrets.toml.example auto_documentation/secrets.toml
   # Edit secrets.toml with your credentials
   ```

### Usage
Example workflow:
1. Configure ticket source (Jira credentials in secrets.toml)
2. Run the system:
   ```bash
   poetry run python -m auto_documentation.main --run-type TEST_CREATE --ticket-source JIRA --ticket-tree-src your_config.yaml --parent-ticket-id YOUR-TICKET-ID
   ```
3. System will:
   - Build ticket tree from parent ticket
   - Generate appropriate prompts
   - Create documentation/test structure

## Configuration
The system uses Dynaconf for configuration management. Key configuration files:

### settings.yaml
Create this file in the root directory:
```yaml
# Jira Configuration
jira_project_url: "https://your-jira-instance.atlassian.net"
jira_project_name: "YOUR_PROJECT"
jira_email: "your-email@company.com"

# Environment Configuration
environment: "development"  # or "production"

# Output Configuration
output_directory: "output"
```

### secrets.toml
Create this file in the auto_documentation directory:
```toml
# Jira API Token (required)
jira_auth = "your-jira-api-token"

# Optional: LLM API Keys (if using external LLM services)
# openai_api_key = "your-openai-key"
# anthropic_api_key = "your-anthropic-key"
```

To set up your configuration:
1. Copy the example files:
   ```bash
   cp settings.yaml.example settings.yaml
   cp auto_documentation/secrets.toml.example auto_documentation/secrets.toml
   ```
2. Edit both files with your specific configuration
3. Ensure secrets.toml is in your .gitignore (it is by default)

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
[License details to be added]
