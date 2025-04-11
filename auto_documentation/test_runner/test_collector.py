import pytest
import time


class ResultsCollector:
    def __init__(self):
        self.reports = []
        self.collected = 0
        self.exitcode = 0
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.total_duration = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_make_report(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == "call":
            self.reports.append(report)

    def pytest_collection_modify_items(self, items):
        self.collected = len(items)

    def pytest_terminal_summary(self, terminal_reporter, exit_status):
        # To do need to add a way to get the file name
        print(exit_status, dir(exit_status))
        self.exitcode = exit_status.value
        self.passed = len(terminal_reporter.stats.get("passed", []))
        self.failed = len(terminal_reporter.stats.get("failed", []))
        self.xfailed = len(terminal_reporter.stats.get("xfailed", []))
        self.skipped = len(terminal_reporter.stats.get("skipped", []))

        self.total_duration = time.time() - terminal_reporter._sessionstarttime
