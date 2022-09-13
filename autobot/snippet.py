import ast
import re
from typing import Generator, List, NamedTuple, Type


def decontextualize(source: str, node: ast.stmt) -> "Snippet":
    """Decontextualize a snippet from its originating source code.

    Takes the originating source code as input, along with the node to decontextualize,
    and extracts the code as a snippet, removing any indentation.
    """
    # Extract the source segment.
    source_segment = ast.get_source_segment(source, node, padded=True)
    assert source_segment, "Unable to find source segment."

    # Dedent the code:.
    # TODO(charlie): This isn't safe. For example, there could be multi-line strings
    # within a function that need this padding.
    lines = source_segment.splitlines()
    if m := re.match(r"(\s+)", lines[0]):
        padding = m.group()
        source_segment = "\n".join([line.removeprefix(padding) for line in lines])
    else:
        padding = ""

    return Snippet(source_segment, padding, node.lineno)


def recontextualize(snippet: "Snippet", source: str) -> list[str]:
    """Recontextualize a snippet within its originating source code.

    Takes the originating source code and snippet as input, and outputs the lines of the
    source code up to and including the snippet, with the snippet adjusted to match the
    indentation of its originating context.
    """
    lines: list[str] = []

    # Prepend any lines of the originating source code that precede the snippet.
    source_lines = source.splitlines()
    if snippet.lineno > 1:
        for i in range(snippet.lineno - 1):
            lines.append(source_lines[i])

    # Tack on the snippet itself, with indentation re-applied.
    for line in snippet.text.splitlines():
        lines.append(snippet.padding + line)

    return lines


class Snippet(NamedTuple):
    """A snippet extracted from source code."""

    text: str
    padding: str
    lineno: int

    @classmethod
    def from_node(cls, source: str, node: ast.stmt) -> "Snippet":
        return decontextualize(source, node)


class ClassDefVisitor(ast.NodeVisitor):
    """NodeVisitor to collect all ClassDef nodes in an AST."""

    def __init__(self) -> None:
        self.nodes: List[ast.ClassDef] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.nodes.append(node)


class FunctionDefVisitor(ast.NodeVisitor):
    """NodeVisitor to collect all FunctionDef nodes in an AST."""

    def __init__(self) -> None:
        self.nodes: List[ast.FunctionDef] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.nodes.append(node)


def iter_snippets(
    source: str,
    node_type: Type[ast.stmt],
) -> Generator[Snippet, None, None]:
    """Generate all snippets from the provided source code.

    Returns: a tuple of (text to fix, any indentation that was removed from the
        snippet, line number in the source file).
    """
    visitor: ClassDefVisitor | FunctionDefVisitor
    if node_type == ast.ClassDef:
        visitor = ClassDefVisitor()
    elif node_type == ast.FunctionDef:
        visitor = FunctionDefVisitor()
    else:
        raise NotImplementedError(f"Unhandled AST node type: {node_type}")

    visitor.visit(ast.parse(source))

    for node in visitor.nodes:
        yield Snippet.from_node(source, node)
