from pathlib import Path
from typing import Union
from auto_documentation.markdown_converter.html_validator import HtmlNode

class HtmlToPdfConverter:
    def __init__(self, html_file_path: Union[Path, str], html_node: HtmlNode):
        self.html_file_path = html_file_path
        self.html_node = html_node

    def convert(self):
        pass
