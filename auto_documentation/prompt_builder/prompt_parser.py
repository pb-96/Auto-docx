from auto_documentation.custom_types import PromptOutput
from pathlib import Path
from typing import Tuple, Union
import json


def parse_prompt_output(prompt_output_path: Union[Path, str]) -> Tuple[Path, Path]:
    ...
