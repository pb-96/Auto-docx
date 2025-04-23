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
Please give the the output using the following format ->

please write a BDD test using Cucumber style scenario linked to a pytest-bdd test  test for the testable ticket which is the leaf of the tree with the following key -> {test_name}
please use python version {python_version}
please name the the python code {src_folder}/{test_name}.py
please name the gherkin file as {src_folder}/{test_name}.feature

please return both the python code and Cucumber file as string in the following dictionary format ->

    python_code: python_code,
    Cucumber_file: Cucumber_file_contents
    output_path: {src_folder}
    key: {test_name}

Then Please convert the above dictionary into a json object and return it as a string

"""


def test_builder_prompt(_dict: TestBuilderPrompt) -> str:
    return TEST_BUILDER_PROMPT.format(**_dict)
