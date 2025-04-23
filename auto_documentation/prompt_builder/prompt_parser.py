from auto_documentation.custom_types import PromptOutput
from pathlib import Path
from typing import Tuple, Union
import json


def parse_prompt_output(prompt_output_path: Union[Path, str]) -> Tuple[Path, Path]:
    if isinstance(prompt_output_path, str):
        prompt_output_path = Path(prompt_output_path)

    prompt_output: PromptOutput = json.loads(prompt_output_path.read_text())
    src_folder = prompt_output["output_path"]
    python_code = prompt_output["python_code"]
    cucumber_file = prompt_output["Cucumber_file"]

    # Create the src folder if it doesn't exist
    src_folder_path = Path(src_folder)
    src_folder_path.mkdir(parents=True, exist_ok=True)

    python_destination = src_folder_path / f"{prompt_output['key']}.py"
    cucumber_destination = src_folder_path / f"{prompt_output['key']}.feature"
    python_destination.write_text(python_code)
    cucumber_destination.write_text(cucumber_file)

    return python_destination, cucumber_destination
