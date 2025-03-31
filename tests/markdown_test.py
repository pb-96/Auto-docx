import unittest

from markdown import (
    parse,
)


class MarkdownTest(unittest.TestCase):
    def test_parses_normal_text_as_a_paragraph(self):
        self.assertEqual(
            parse("This will be a paragraph"), "<p>This will be a paragraph</p>"
        )

    def test_parsing_italics(self):
        self.assertEqual(
            parse("_This will be italic_"), "<p><em>This will be italic</em></p>"
        )

    def test_parsing_bold_text(self):
        self.assertEqual(
            parse("__This will be bold__"), "<p><strong>This will be bold</strong></p>"
        )

    def test_mixed_normal_italics_and_bold_text(self):
        self.assertEqual(
            parse("This will _be_ __mixed__"),
            "<p>This will <em>be</em> <strong>mixed</strong></p>",
        )

    def test_with_h1_header_level(self):
        self.assertEqual(parse("# This will be an h1"), "<h1>This will be an h1</h1>")

    def test_with_h2_header_level(self):
        self.assertEqual(parse("## This will be an h2"), "<h2>This will be an h2</h2>")

    def test_with_h3_header_level(self):
        self.assertEqual(parse("### This will be an h3"), "<h3>This will be an h3</h3>")

    def test_with_h4_header_level(self):
        self.assertEqual(
            parse("#### This will be an h4"), "<h4>This will be an h4</h4>"
        )

    def test_with_h5_header_level(self):
        self.assertEqual(
            parse("##### This will be an h5"), "<h5>This will be an h5</h5>"
        )

    def test_with_h6_header_level(self):
        self.assertEqual(
            parse("###### This will be an h6"), "<h6>This will be an h6</h6>"
        )

    def test_h7_header_level_is_a_paragraph(self):
        self.assertEqual(
            parse("####### This will not be an h7"),
            "<p>####### This will not be an h7</p>",
        )

    def test_unordered_lists(self):
        self.assertEqual(
            parse("* Item 1\n* Item 2"), "<ul><li>Item 1</li><li>Item 2</li></ul>"
        )

    def test_with_markdown_symbols_in_the_header_text_that_should_not_be_interpreted(
        self,
    ):
        self.assertEqual(
            parse("# This is a header with # and * in the text"),
            "<h1>This is a header with # and * in the text</h1>",
        )

    def test_with_a_little_bit_of_everything(self):
        self.assertEqual(
            parse("# Header!\n* __Bold Item__\n* _Italic Item_"),
            "<h1>Header!</h1><ul><li><strong>Bold Item</strong></li><li><em>Italic Item</em></li></ul>",
        )

    def test_with_markdown_symbols_in_the_list_item_text_that_should_not_be_interpreted(
        self,
    ):
        self.assertEqual(
            parse("* Item 1 with a # in the text\n* Item 2 with * in the text"),
            "<ul><li>Item 1 with a # in the text</li><li>Item 2 with * in the text</li></ul>",
        )

    def test_unordered_lists_close_properly_with_preceding_and_following_lines(self):
        self.assertEqual(
            parse("# Start a list\n* Item 1\n* Item 2\nEnd a list"),
            "<h1>Start a list</h1><ul><li>Item 1</li><li>Item 2</li></ul><p>End a list</p>",
        )

    def test_with_markdown_symbols_in_the_paragraph_text_that_should_not_be_interpreted(
        self,
    ):
        self.assertEqual(
            parse("This is a paragraph with # and * in the text"),
            "<p>This is a paragraph with # and * in the text</p>",
        )

    def test_table(self):
        table = """
| Header 1 | Header 2 |
| -------- | -------- |
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        expected = "<table><tr><th>Header 1</th><th>Header 2</th></tr><tr><td>Cell 1</td><td>Cell 2</td></tr><tr><td>Cell 3</td><td>Cell 4</td></tr></table>"
        self.assertEqual(parse(table), expected)

    def test_complex_markdown_file(self):
        with open("tests/large_markdown_file.md", "r") as file:
            text = file.read()

        self.assertEqual(parse(text), """<h1>This is the main section of the document.</h1><h2>Table Section</h2><table><tr><th>Header 1</th><th>Header 2</th></tr><tr><td>Cell 1</td><td>Cell 2</td></tr><tr><td>Cell 3</td><td>Cell 4</td></tr></table><h3>It can have Nested headers</h3><p>This content belongs specifically to the nested header section.</p><p>But can't quite group stuff together yet</p><h2>Special Characters Section</h2><p>This is a paragraph with # and * in the text</p><h2>List Section</h2><ul><li>Item 1 with a # in the text</li><li>Item 2 with * in the text</li></ul><h2>Do you end lists correctly</h2><p>This is a paragraph with # and * in the text after the list section</p>""")
