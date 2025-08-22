from pathlib import Path
from typing import Union
from typing import Dict


class TestRunnerBase:
    def validate(self) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    def run_tests(self) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    def build_test_paths(self) -> list[Path]:
        raise NotImplementedError("Subclasses must implement this method")


class TestRunnerFromFolder(TestRunnerBase):
    def __init__(self, src_folder: Union[str, Path], testable_keys: list[str]):
        self.src_folder = src_folder
        self.testable_keys = testable_keys
        self.validate()
        self.testable_paths = self.build_test_paths()

    def validate(self) -> None:
        if not Path(self.src_folder).exists():
            raise FileNotFoundError(f"The folder {self.src_folder} does not exist")
        if not Path(self.src_folder).is_dir():
            raise NotADirectoryError(f"The path {self.src_folder} is not a directory")
        if isinstance(self.src_folder, str):
            self.src_folder = Path(self.src_folder)
        folder_contents = {src.name for src in self.src_folder.iterdir()}
        if not all(key in folder_contents for key in self.testable_keys):
            raise ValueError(
                f"The folder {self.src_folder} does not contain all the testable keys: {self.testable_keys}"
            )

    def build_test_paths(self) -> list[Path]:
        return [self.src_folder / key for key in self.testable_keys]

    def run_tests(self) -> None: ...


class TestRunnerFactory:
    test_runner_instances: Dict[str, TestRunnerBase]

    def __new__(cls, *args, **kwargs): ...
