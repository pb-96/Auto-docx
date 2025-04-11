from auto_documentation.custom_types import TestBuilderPrompt

TEST_BUILDER_PROMPT = """
You are a test builder. You are given a ticket tree and a ticket id. You need to build a test for the ticket.
You are given a tree structure where the parent structure is as below -> with the leaf need being the actual test that needs to be built.
@Outline Tree Structure from parent to leaf
{tree_structure}
Where the parent ticket type is {parent_ticket_type} and the child ticket type is {child_ticket_type}
These are the ticket descriptions for the tickets from parent to leaf
{ticket_descriptions}
You need to build a test for the child ticket.
You need to build a test that is as close to the ticket description as possible.
Please use the python library pytest-bdd for this test.
Please give the the output using the following format ->
You should return the test using python {python_version} code.
Please return the test in a single function 
Please name the test function as {test_name}
"""


def build_test_builder_prompt(_dict: TestBuilderPrompt) -> str:
    return TEST_BUILDER_PROMPT.format(**_dict)
