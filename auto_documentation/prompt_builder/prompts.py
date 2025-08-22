# BDD Behavior Tree Prompt System
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

# ============================================================================
# BEHAVIOR TREE GENERATION PROMPTS
# ============================================================================

BEHAVIOR_TREE_GENERATION_PROMPT = """
You are a behavior tree architect for BDD test execution. Given a ticket tree structure, generate a behavior tree that orchestrates BDD test creation and execution.

TICKET TREE STRUCTURE:
{ticket_tree_structure}

TICKET DESCRIPTIONS:
{ticket_descriptions}

REQUIREMENTS:
1. Create a behavior tree that validates ticket structure
2. Process each testable ticket (leaf nodes) 
3. Generate BDD scenarios for each testable ticket
4. Execute tests in dependency order
5. Collect and report results

AVAILABLE NODE TYPES:
- "sequence": Execute all children in order, fail if any child fails
- "selector": Execute children until one succeeds
- "action": Execute a specific action
- "condition": Check a condition and return success/failure

AVAILABLE ACTIONS:
- "validate_ticket_structure": Check if ticket hierarchy is valid
- "generate_bdd_scenario": Create Gherkin scenarios from ticket
- "execute_bdd_test": Run pytest-bdd test
- "collect_test_results": Gather test execution results
- "generate_test_report": Create test execution report

Return a JSON structure representing the behavior tree:
{{
    "root": {{
        "type": "sequence",
        "name": "bdd_test_orchestrator",
        "children": [
            {{
                "type": "action",
                "name": "validate_ticket_structure",
                "action": "validate_ticket_structure"
            }},
            {{
                "type": "sequence", 
                "name": "process_testable_tickets",
                "children": [
                    // Your generated nodes here
                ]
            }}
        ]
    }}
}}
"""

# ============================================================================
# BDD SCENARIO GENERATION PROMPTS
# ============================================================================

BDD_SCENARIO_GENERATION_PROMPT = """
You are a BDD test scenario generator. Create comprehensive Gherkin scenarios based on ticket descriptions.

TICKET INFORMATION:
- Ticket Key: {ticket_key}
- Ticket Type: {ticket_type}
- Title: {ticket_title}
- Description: {ticket_description}

PARENT CONTEXT:
{parent_context}

REQUIREMENTS:
1. Create realistic, testable BDD scenarios
2. Use proper Gherkin syntax (Given/When/Then)
3. Include edge cases and error scenarios
4. Make scenarios specific to the ticket requirements
5. Consider the parent ticket context for integration scenarios

SCENARIO STRUCTURE:
- Feature: Descriptive feature name
- Background: Common setup steps (if needed)
- Scenario: Main happy path
- Scenario Outline: Parameterized scenarios (if applicable)
- Examples: Test data for scenario outlines

Return both the Gherkin feature file and corresponding pytest-bdd implementation:

FEATURE FILE (.feature):
```gherkin
Feature: [Feature Name]
  As a [user role]
  I want [functionality]
  So that [benefit]

  Scenario: [Scenario Name]
    Given [precondition]
    When [action]
    Then [expected result]
```

PYTEST-BDD IMPLEMENTATION (.py):
```python
from pytest_bdd import scenarios, given, when, then, parsers
import pytest

scenarios('path/to/feature.feature')

@given('precondition')
def precondition():
    # Implementation
    pass

@when('action')
def action():
    # Implementation
    pass

@then('expected result')
def expected_result():
    # Implementation
    pass
```

Return as JSON:
{{
    "feature_file": "gherkin content",
    "python_implementation": "pytest-bdd code",
    "test_name": "{ticket_key}_test",
    "feature_name": "descriptive_feature_name"
}}
"""

# ============================================================================
# TEST EXECUTION ORCHESTRATION PROMPTS
# ============================================================================

TEST_EXECUTION_PROMPT = """
You are a BDD test execution orchestrator. Given a behavior tree and test results, determine the next execution steps.

BEHAVIOR TREE:
{behavior_tree}

CURRENT EXECUTION STATE:
{execution_state}

TEST RESULTS:
{test_results}

AVAILABLE ACTIONS:
- "retry_failed_tests": Re-run failed tests with different parameters
- "skip_dependent_tests": Skip tests that depend on failed tests
- "generate_error_report": Create detailed error report
- "continue_execution": Proceed with remaining tests
- "abort_execution": Stop all test execution

DECISION CRITERIA:
1. If critical tests fail, abort execution
2. If non-critical tests fail, continue with retry logic
3. If dependent tests fail, skip downstream tests
4. If all tests pass, generate success report

Return execution decision as JSON:
{{
    "next_action": "action_name",
    "reason": "explanation",
    "affected_tests": ["test1", "test2"],
    "execution_plan": {{
        "retry_count": 0,
        "skip_tests": [],
        "continue_tests": []
    }}
}}
"""

# ============================================================================
# PYDANTIC CONTEXT MODELS
# ============================================================================


class TicketData(BaseModel):
    """Ticket information for BDD scenario generation"""

    key: str = Field(..., description="Ticket key/ID")
    ticket_type: str = Field(
        ..., description="Type of ticket (Epic, Story, Task, etc.)"
    )
    title: str = Field(..., description="Ticket title")
    description: str = Field(..., description="Ticket description")
    parent_context: Optional[str] = Field(
        default="", description="Parent ticket context"
    )

    def to_prompt_context(self) -> Dict[str, str]:
        """Convert to format expected by prompt templates"""
        return {
            "ticket_key": self.key,
            "ticket_type": self.ticket_type,
            "ticket_title": self.title,
            "ticket_description": self.description,
            "parent_context": self.parent_context or "",
        }


class TreeContext(BaseModel):
    """Context for behavior tree generation"""

    ticket_tree_structure: str = Field(
        ..., description="String representation of ticket tree"
    )
    ticket_descriptions: Dict[str, Any] = Field(
        ..., description="Ticket descriptions dictionary"
    )

    def to_prompt_context(self) -> Dict[str, str]:
        """Convert to format expected by prompt templates"""
        return {
            "ticket_tree_structure": self.ticket_tree_structure,
            "ticket_descriptions": str(self.ticket_descriptions),
        }


class ExecutionContext(BaseModel):
    """Context for test execution orchestration"""

    behavior_tree: Dict[str, Any] = Field(..., description="Behavior tree structure")
    execution_state: Dict[str, Any] = Field(..., description="Current execution state")
    test_results: Dict[str, Any] = Field(..., description="Test execution results")

    def to_prompt_context(self) -> Dict[str, str]:
        """Convert to format expected by prompt templates"""
        return {
            "behavior_tree": str(self.behavior_tree),
            "execution_state": str(self.execution_state),
            "test_results": str(self.test_results),
        }


class TestResult(BaseModel):
    """Individual test result"""

    test_name: str = Field(..., description="Name of the test")
    status: str = Field(..., description="Test status (PASS/FAIL/SKIP)")
    duration: float = Field(..., description="Test execution duration")
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    output: Optional[str] = Field(default=None, description="Test output")


class ExecutionPlan(BaseModel):
    """Test execution plan"""

    retry_count: int = Field(default=0, description="Number of retries attempted")
    skip_tests: List[str] = Field(default_factory=list, description="Tests to skip")
    continue_tests: List[str] = Field(
        default_factory=list, description="Tests to continue with"
    )
    max_retries: int = Field(default=3, description="Maximum number of retries")


class ExecutionDecision(BaseModel):
    """Decision made by execution orchestrator"""

    next_action: str = Field(..., description="Next action to take")
    reason: str = Field(..., description="Reason for the decision")
    affected_tests: List[str] = Field(
        default_factory=list, description="Tests affected by decision"
    )
    execution_plan: ExecutionPlan = Field(..., description="Updated execution plan")


# ============================================================================
# PROMPT HELPER FUNCTIONS
# ============================================================================


def generate_behavior_tree_prompt(context: TreeContext) -> str:
    """Generate behavior tree from ticket structure"""
    return BEHAVIOR_TREE_GENERATION_PROMPT.format(**context.to_prompt_context())


def generate_bdd_scenario_prompt(context: TicketData) -> str:
    """Generate BDD scenarios from ticket description"""
    return BDD_SCENARIO_GENERATION_PROMPT.format(**context.to_prompt_context())


def generate_execution_prompt(context: ExecutionContext) -> str:
    """Generate test execution orchestration prompt"""
    return TEST_EXECUTION_PROMPT.format(**context.to_prompt_context())


# ============================================================================
# FACTORY METHODS FOR EASY CREATION
# ============================================================================


def create_ticket_context(
    key: str,
    ticket_type: str,
    title: str,
    description: str,
    parent_context: Optional[str] = None,
) -> TicketData:
    """Create TicketData from individual fields"""
    return TicketData(
        key=key,
        ticket_type=ticket_type,
        title=title,
        description=description,
        parent_context=parent_context,
    )


def create_tree_context(ticket_tree: Any, descriptions: Dict[str, Any]) -> TreeContext:
    """Create TreeContext from ticket tree and descriptions"""
    return TreeContext(
        ticket_tree_structure=str(ticket_tree), ticket_descriptions=descriptions
    )


def create_execution_context(
    behavior_tree: Dict[str, Any],
    execution_state: Dict[str, Any],
    test_results: Dict[str, Any],
) -> ExecutionContext:
    """Create ExecutionContext from execution data"""
    return ExecutionContext(
        behavior_tree=behavior_tree,
        execution_state=execution_state,
        test_results=test_results,
    )
