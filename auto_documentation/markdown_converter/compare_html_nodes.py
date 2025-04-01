from .html_validator import HtmlNode


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