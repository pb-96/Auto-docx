from collections import deque
from typing import List, Deque, cast, Optional, Union
from pathlib import Path
from enum import Enum
import re
from collections import deque


class SupportedTags(Enum):
    TABLE = "table"
    TR = "tr"
    TH = "th"
    TD = "td"
    UL = "ul"
    LI = "li"
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    H6 = "h6"
    P = "p"
    STRONG = "strong"
    EM = "em"
    DIV = "div"
    SPAN = "span"
    IMG = "img"
    A = "a"
    BR = "br"
    HR = "hr"
    BODY = "body"
    HEADER = "header"


MEMBER_SET = {v.value for v in SupportedTags._value2member_map_.values()}


class HtmlNode:
    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.text = re.sub("[^a-z0-9]+", "", tag)
        # This will throw an error if the raw text is not a member of supported tags
        self.enum_value = SupportedTags(self.text)
        self.content: Union[str, None] = None
        self.children: List[HtmlNode] = []
        self.parent: Optional[HtmlNode] = None
        self.closed = False

    def __repr__(self) -> str:
        return f"tag={self.tag}, closed={self.closed}, parent={self.parent.tag if self.parent else 'Root'} , Children={self.children}"

    def __str__(self) -> str:
        return self.__repr__()

    def compare_close(self, other: "HtmlNode") -> bool:
        return (
            self.text == other.text
            and self.tag.startswith("<")
            and other.tag.startswith("</")
        )

    def is_root(self):
        return len(self.parent) == 0

    def compare_root(self, other: "HTMLProcessor") -> bool:
        return id(self) == id(other.root)

    def display_string(self, indent: int = 4) -> str:
        result = f"{indent * ' '}{self.tag}\n"
        if self.content:
            result += indent * " " + self.content + "\n"

        for child in self.children:
            result += indent * " " + child.tag + "\n"
            if child.content:
                result += indent * " " + child.content + "\n"
            # Add content here if applicable
            for next_child in child.children:
                result += next_child.display_string(indent + 4)
            result += indent * " " + f"{child.tag.replace('<', '</')}\n"
        result += f"{indent * ' '}{self.tag.replace('<', '</')}\n"
        return result

    def write_to_file(self, file_path: Path):
        if file_path.suffix != ".html":
            raise ValueError("File path must be a valid HTML file")

        with open(file_path, "w") as f:
            f.write(self.display_string())


class HTMLProcessor:
    def __init__(self, html: str):
        self.html = html
        self.member_set = set(
            [value.value for value in SupportedTags._member_map_.values()]
        )
        self.in_tag = False
        self.current_tag = ""
        self.current_content = ""
        self.stack: Deque[HtmlNode] = deque()
        self.root: Optional[HtmlNode] = None
        self.node_tracker: Optional[HtmlNode] = None
        self.valid = self.validate()

    def process_tag(self, char: str) -> bool:
        self.in_tag = False
        self.current_tag += char
        stripped_tag = re.sub("[^a-z0-9]+", "", self.current_tag)
        if stripped_tag not in self.member_set:
            raise ValueError(
                f"Invalid tag: {self.current_tag} stripped_to: {stripped_tag}"
            )
        elif self.current_tag.startswith("</"):
            if not self.stack:
                return False

            last = cast(HtmlNode, self.stack.pop())
            last.content = self.current_content
            current_node = HtmlNode(self.current_tag)

            if not last.compare_close(current_node):
                return False

            last.closed = True
            if last.parent is not None:
                self.node_tracker = last.parent
            else:
                self.node_tracker = last

        elif self.current_tag.startswith("<"):
            current_node = HtmlNode(self.current_tag)
            if self.root is None:
                self.root = HtmlNode("<body>")
                self.root.children.append(current_node)
                self.node_tracker = current_node
                self.node_tracker.parent = self.root
            else:
                self.node_tracker.children.append(current_node)
                current_node.parent = self.node_tracker
                self.node_tracker = current_node

            self.stack.append(current_node)

        self.root.closed = True
        self.current_tag = ""
        return True

    def get_tags(self) -> bool:
        for char in self.html:
            if char == "<":
                self.in_tag = True
                self.current_tag += char
            elif char == ">":
                matched = self.process_tag(char)
                if not matched:
                    return False
                self.current_content = ""
            elif self.in_tag:
                self.current_tag += char
            elif not self.in_tag:
                self.current_content += char
        return len(self.stack) == 0

    def validate(self) -> bool:
        all_tags_stack_empty = self.get_tags()
        validate_further = check_valid(self.root)
        return all_tags_stack_empty and validate_further

    def __repr__(self):
        return self.root.display_string()


def compare_nodes_equal(left: HtmlNode, right: HtmlNode) -> bool:
    if left.tag != right.tag:
        return False

    if left.children and not right.children:
        return False

    if right.children and not left.children:
        return False

    if len(right.children) != len(left.children):
        return False

    for left_child, right_child in zip(left.children, right.children):
        if not compare_nodes_equal(left_child, right_child):
            return False

    return True


def check_valid(html_node: HtmlNode) -> bool:
    if not html_node.closed:
        return False

    children = html_node.children
    if children:
        queue = deque(children)
        while queue:
            next_child = queue.popleft()
            if not next_child.closed:
                return False
            for _child in next_child.children:
                queue.append(_child)
    return True
