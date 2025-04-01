import unittest
from pathlib import Path
from auto_documentation.markdown_converter.html_validator import (
    HTMLProcessor,
    HtmlNode
)
from auto_documentation.markdown_converter.compare_html_nodes import (
    compare_nodes_equal
)
from auto_documentation.markdown_converter.markdown import (
    parse,
)


class HtmlValidatorTest(unittest.TestCase):
    def test_complex_html(self):
        COMPLEX_DATA = Path("tests/test_data/test.html").read_text()
        AS_HTML = HTMLProcessor(COMPLEX_DATA).root
        is_equal = compare_nodes_equal(AS_HTML, AS_HTML)
        assert is_equal
    
    def test_not_equal(self):
        COMPLEX_DATA = Path("tests/test_data/test.html").read_text()
        AS_HTML = HTMLProcessor(COMPLEX_DATA).root
        SIMPLE_DATA = Path("tests/test_data/simple.html").read_text()
        AS_OTHER = HTMLProcessor(SIMPLE_DATA).root

        not_equal = compare_nodes_equal(AS_HTML, AS_OTHER)
        assert not not_equal

    def test_complex_string(self):
        MARKDOWN_DATA = Path("tests/test_data/large_markdown_file.md").read_text()
        COMPLEX_DATA = Path("tests/test_data/test.html").read_text()
        as_html = parse(MARKDOWN_DATA)
        as_html_node = HTMLProcessor(as_html).root
        AS_HTML = HTMLProcessor(COMPLEX_DATA).root

        
        

