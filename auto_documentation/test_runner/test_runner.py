from pathlib import Path
from typing import Union


class TestRunner:
    def __init__(self, src_folder: Union[str, Path]):
        self.src_folder = src_folder
