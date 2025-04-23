from docx import Document
from pathlib import Path
from typing import Union
from auto_documentation.markdown_converter.html_validator import HtmlNode, SupportedTags


class HtmlToWordConverter:
    def __init__(
        self,
        html_file_path: Union[Path, str, None],
        html_node: Union[HtmlNode, None],
        test_output_path: Union[Path, str, None],
    ):
        self.html_file_path = html_file_path
        self.html_node = html_node
        self.supported_tags = SupportedTags
        self.test_output_path = test_output_path
        self.doc = Document()

        if self.html_file_path and self.html_node is None:
            self.open_html_file()

        self.convert()
        self.save_to_file(self.test_output_path)

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
            match child.tag:
                case ():
                    ...

            if child.children:
                self.recursive_convert(child)

    def convert(self):
        try:
            # Process root node
            self.recursive_convert(self.html_node)
            # This meant it ran without errors
            return True
        except Exception as e:
            raise e

    def get_doc(self):
        return self.doc

    def convert_to_bytes(self): ...

    def save_to_file(self, file_path: Union[Path, str]): ...
