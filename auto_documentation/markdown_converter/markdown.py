from typing import Dict, List, Generator, Union
from collections import deque
import re
from dataclasses import dataclass, field


@dataclass
class MarkdownState:
    in_list: bool = False
    in_header: str = ""
    chars: List[str] = field(default_factory=list)
    open_tags: List[str] = field(default_factory=list)
    all_tokens: List[str] = field(default_factory=list)
    all_text: List[str] = field(default_factory=list)
    last_token: str = ""
    all_tags = deque()
    in_table: bool = False
    last_header: bool = False

    def process_line(self, text: str) -> None:
        self.last_token = ""
        self.chars = []
        self.all_tokens = []
        self.in_header = ""
        self.all_text.append(text)


class HTMLTag:
    UNDERSCORE = "_"
    HASH = "#"
    ASTERISK = "*"
    AT = "@"
    SPACE = " "
    PIPE = "|"
    # Group related tags
    INLINE_TAGS = {
        UNDERSCORE: "em",
        UNDERSCORE * 2: "strong",
    }

    BLOCK_TAGS = {
        HASH: "h1",
        ASTERISK: "ul",
        "in_list": "li",
        PIPE: "table",
        "in_table": "tr",
        "in_header": "th",
        "in_cell": "td",
    }
    TAGS = {**INLINE_TAGS, **BLOCK_TAGS}

    TAG_PRIORITY = {
        "li": 1,
        "ul": 2,
        "em": 1,
        "strong": 1,
        "h1": 0,
        "h2": 0,
        "h3": 0,
        "h4": 0,
        "h5": 0,
        "h6": 0,
        "table": 0,
        "tr": 0,
        "td": 0,
        "th": 0,
    }


class MarkDownParser:
    def __init__(self, mapping: Dict[str, str] = HTMLTag.TAGS, upper_lim: int = 6):
        self.mapping = mapping
        self.upper_lim = upper_lim
        self.state = MarkdownState()

    def parse_header(self, text: str):
        length = len(text)
        if length > self.upper_lim:
            return text

        return self.mapping.get("#") * length

    def __process_header(self, char: str) -> None:
        if len(self.state.all_tags):
            tag_number = int("".join(re.findall(r"\d", self.state.all_tags[-1])))
            if (tag_number + 1) < self.upper_lim + 1:
                self.state.all_tags[-1] = f"h{tag_number + 1}"
                self.state.in_header += "#"
            else:
                self.state.chars.append(self.state.in_header + char)
                self.state.in_header = ""
                self.state.all_tags.pop()
        else:
            self.state.chars[-1] = self.state.chars[-1] + char

    def process_header(self, char: str) -> None:
        if not self.state.in_list:
            self.__process_header(char)
        else:
            self.state.chars.append(char)

    def process_list(self, char) -> None:
        empty_chars = not self.state.chars
        if not self.state.in_list and empty_chars:
            self.state.in_list = True
            self.state.all_tags.append(self.mapping.get(char))
            self.process_tags()
            self.state.all_tags.append(self.mapping.get("in_list"))
        elif empty_chars:
            self.state.all_tags.append(self.mapping.get("in_list"))
        else:
            self.state.chars.append(char)

    def __init_header(self, char: str) -> None:
        if not self.state.chars:
            if not self.state.in_header:
                self.state.in_header = "#"
                self.state.all_tags.append(self.mapping.get(char))
            else:
                self.state.chars.append(char)
        else:
            self.state.chars.append(char)

    def append_tags(self, char: str) -> None:
        match (char, self.state.last_token):
            case ("_", "_"):
                if len(self.state.all_tags):
                    self.state.all_tags.pop()
                self.state.all_tags.append(
                    self.mapping.get(char + self.state.last_token)
                )
            case ("_", self.state.last_token):
                mapped = self.mapping.get(char)
                self.state.all_tags.append(mapped)
            case ("#", "#"):
                self.process_header(char)
            case ("#", self.state.last_token):
                self.__init_header(char)
            case ("*", self.state.last_token):
                self.process_list(char)

    def process_tags(self) -> None:
        middle_string = "".join(self.state.chars)
        if self.state.in_table:
            middle_string = middle_string.strip()
        elif middle_string != " ":
            middle_string = middle_string.lstrip()

        empty = len(middle_string) == 0
        if not empty:
            self.state.all_tokens.append(middle_string)

        for token in sorted(
            self.state.all_tags, key=lambda k: HTMLTag.TAG_PRIORITY.get(k)
        ):
            if token not in self.state.open_tags:
                self.state.all_tokens.append(f"<{token}>")
                self.state.open_tags.append(token)
            else:
                self.state.all_tokens.append(f"</{token}>")
                self.state.open_tags.remove(token)
        self.state.all_tags.clear()

    def process_end(self) -> None:
        header_no = len(self.state.in_header)
        if header_no:
            closing = f"h{header_no}"
            self.state.all_tags.append(closing)
        elif self.state.in_list:
            self.state.all_tags.append(self.mapping.get("in_list"))
        elif self.state.in_table:
            self.state.all_tags.append(self.mapping.get("in_table"))

    def cleanup(self) -> None:
        self.state = MarkdownState()

    def parse_final_string(self) -> str:
        string = "".join(self.state.all_tokens)
        if (
            string.startswith("<table")
            or string.startswith("<tr")
            or string.startswith("<th")
            or string.startswith("<td")
            or string.startswith("<h")
            or string.startswith("<ul")
            or string.startswith("<p")
            or string.startswith("<li")
            or string.startswith("<tr")
            or string.startswith("<td")
            or string.startswith("<th")
        ):
            return string
        return f"<p>{string}</p>"

    def header_in_text(self, char: str) -> bool:
        return (
            char == HTMLTag.SPACE
            and self.state.last_token == HTMLTag.HASH
            and len(self.state.in_header) > 0
            and not self.state.chars
        )

    def list_in_text(self, char):
        return (
            char == HTMLTag.SPACE
            and self.state.last_token == HTMLTag.ASTERISK
            and self.state.in_list
            and not self.state.chars
        )

    def process_table_start(self) -> None:
        if not self.state.in_table:
            self.state.in_table = True
            self.state.last_header = True
            self.state.all_tags.append(self.mapping.get(HTMLTag.PIPE))
            self.state.all_tags.append(self.mapping.get("in_table"))
            self.state.all_tags.append(self.mapping.get("in_header"))
        else:
            self.state.all_tags.append(self.mapping.get("in_table"))
            self.state.all_tags.append(self.mapping.get("in_cell"))

    def process_table_end(self) -> None:
        self.state.in_table = False
        self.state.all_text.append("</table>")

    def process_in_table(self, last: bool) -> None:
        mapped = (
            self.mapping.get("in_header")
            if self.state.last_header
            else self.mapping.get("in_cell")
        )
        if not last:
            self.state.all_tags.append(mapped)
            self.state.all_tags.append(mapped)
        else:
            self.state.all_tags.append(mapped)

    def process_in_list(self, char: str) -> None:
        self.state.in_list = False
        self.state.all_text.append("</ul>")
        self.state.chars.append(char)

    def list_end(self) -> None:
        self.state.in_list = False
        self.state.all_text.append("</ul>")

    def match_char(self, char, start, last):
        if char == HTMLTag.AT:
            self.process_end()
        elif start and char == HTMLTag.PIPE:
            self.process_table_start()
        elif len(self.state.chars) > 0 and char == HTMLTag.PIPE:
            self.process_in_table(last)
        elif self.list_in_text(char):
            return
        elif char in self.mapping:
            self.append_tags(char)
        elif start and self.state.in_list:
            self.process_in_list(char)
        elif len(self.state.all_tags):
            self.process_tags()
            self.state.chars = [char]
        else:
            self.state.chars.append(char)

    def __parse_text(self, given_text: str) -> Union[str, None]:
        if self.state.last_header:
            self.state.last_header = False
            return None
        is_last = lambda index: index == len(given_text) - 2
        for index, char in enumerate(given_text):
            start = index == 0
            last = is_last(index)
            if start:
                if char != HTMLTag.PIPE and self.state.in_table:
                    self.process_table_end()
                if char != HTMLTag.ASTERISK and self.state.in_list:
                    self.list_end()
            # Block match here
            self.match_char(char, start, last)
            self.state.last_token = char
        if self.state.chars:
            self.process_tags()
        return self.parse_final_string()

    def parse(self, given_text: str) -> Generator[List[str], None, None]:
        if not given_text:
            raise ValueError("Empty text provided")
        try:
            for line in given_text.split("\n"):
                if not line:
                    continue
                self.state.process_line(self.__parse_text(line + HTMLTag.AT))

            yield self.state.all_text
        finally:
            self.cleanup()


def parse(text: str, md: Union[MarkDownParser, None] = None):
    joined = ""
    if md is None:
        md = MarkDownParser()

    for line in md.parse(text):
        for text in line:
            joined += text if text is not None else ""
    return joined
