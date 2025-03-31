from docx import Document
from pathlib import Path
from typing import Union
from auto_documentation.markdown_converter.html_validator import HtmlNode, SupportedTags
from enum import Enum

class HtmlToWordConverter:
    def __init__(
        self,
        html_file_path: Union[Path, str, None],
        html_node: Union[HtmlNode, None],
        supported_tags: Union[SupportedTags, Enum],
        test_output_path: Union[Path, str, None],
    ):
        self.html_file_path = html_file_path
        self.html_node = html_node
        self.supported_tags = SupportedTags
        self.test_output_path = test_output_path

        if self.html_file_path and self.html_node is None:
            self.open_html_file()

    def open_html_file(self):
        if not self.html_file_path.absolute():
            raise ValueError("HTML file path must be absolute")
        if not self.html_file_path.exists():
            raise ValueError("HTML file path must exist")
        if not self.html_file_path.is_file():
            raise ValueError("HTML file path must be a file")
        if self.html_file_path.suffix != ".html":
            raise ValueError("HTML file path must have a .html extension")

        raw_data = self.html_file_path.read_text()
        self.html_node = HtmlNode(raw_data)

    def recursive_convert(self, node: HtmlNode):
        for child in node.children:
            match child.type:
                case _:
                    raise ValueError(f"Unsupported node type: {child.type}")

            # Process Child Node here
            if child.children:
                self.recursive_convert(child)

    def convert(self):
        # Process root node
        self.recursive_convert(self.html_node)
