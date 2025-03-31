# BDD Test Generator

## Overview
A test automation framework that leverages LLM (Large Language Models) to generate Behavior-Driven Development (BDD) tests from Jira and Notion tickets. The system features advanced document processing capabilities, converting both Markdown and HTML inputs into structured node types for consistent test generation and documentation.

## Features (Planned)
- Automated BDD test generation from:
  - Jira tickets
  - Notion documents
- Document Processing
  - Markdown to HTML conversion
  - HTML parsing and validation
  - Custom node type generation for:
    - Requirements
    - Test scenarios
    - Expected outcomes
    - Non-functional criteria
- LLM-powered test generation
  - Automatic conversion of requirements to test code
  - Intelligent test case creation based on ticket context
  - Test naming convention matching ticket IDs
- Integration of functional and non-functional requirements
- Celery-based test execution
- Automated documentation generation from:
  - Source tickets
  - Test execution results

## How It Works
1. **Document Processing Pipeline**
   ```mermaid
   graph LR
       A[Input Document] --> B{Format Type}
       B -->|Markdown| C[MD to HTML Converter]
       B -->|HTML| D[HTML Parser]
       C --> D
       D --> E[Node Type Generator]
       E --> F[Document Creator]
   ```

2. **Node Type System**
   - Custom node types for structured representation:
     ```typescript
     interface DocumentNode {
       type: NodeType;
       content: string;
       children: DocumentNode[];
       metadata: NodeMetadata;
     }

     enum NodeType {
       REQUIREMENT,
       TEST_SCENARIO,
       EXPECTED_OUTCOME,
       NFR_CRITERIA,
       // ...
     }
     ```

3. **Input Sources**
   - Jira epics and associated tickets
   - Notion documents
   - Requirements mapping (functional & non-functional)
   - Supported formats:
     - Markdown
     - HTML
     - Plain text

4. **Document Processing**
   - Markdown Processing:
     - Parses markdown syntax
     - Converts to standardized HTML
     - Preserves document structure
   - HTML Processing:
     - Validates HTML structure
     - Extracts relevant content
     - Maps to custom node types
   - Node Generation:
     - Creates structured representation
     - Maintains relationship hierarchy
     - Attaches metadata

5. **LLM Test Generation**
   - Uses processed node types as input
   - Generates Celery test files with:
     - Test names matching ticket IDs
     - BDD-style test structure
     - Appropriate assertions and validations

## Technical Architecture
- **Document Processing Layer**
  - Markdown parser
  - HTML validator
  - Node type generator
  - Document creator

- **Input Processing**
  - Jira/Notion API integration
  - Requirement parser
  - LLM context preparation

- **Test Generation Engine**
  - LLM integration layer
  - Test template system
  - Celery task generator
  - Naming convention manager

- **Execution Framework**
  - Celery worker configuration
  - Test runner
  - Result collector
  - Reporting system

## Example Node Type Usage
```python
# Example of processed document structure
document = {
    "type": "REQUIREMENT",
    "content": "User Authentication",
    "children": [
        {
            "type": "TEST_SCENARIO",
            "content": "Valid Login Flow",
            "children": [
                {
                    "type": "EXPECTED_OUTCOME",
                    "content": "User successfully authenticated"
                }
            ]
        },
        {
            "type": "NFR_CRITERIA",
            "content": "Response time < 200ms"
        }
    ]
}
```

## Getting Started
(To be added)

## Prerequisites
(To be added)

## Installation
(To be added)

## Usage
Example workflow:
1. Configure ticket source (Jira/Notion)
2. System processes input documents:
   - Converts Markdown to HTML if needed
   - Parses HTML into node types
   - Validates document structure
3. System automatically:
   - Generates Celery tests via LLM
   - Names tests according to ticket IDs
   - Creates test documentation
4. Execute tests through Celery
5. View results and generated documentation

## Configuration
(To be added)

## Contributing
(To be added)

## License
(To be added)
