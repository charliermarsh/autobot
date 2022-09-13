import ast
import enum
from typing import Type


class TransformType(enum.Enum):
    CLASS = "Class"
    FUNCTION = "Function"

    def plaintext_name(self) -> str:
        if self == TransformType.CLASS:
            return "class"
        if self == TransformType.FUNCTION:
            return "function"
        raise NotImplementedError(f"Unhandled transform type: {self}")

    def ast_node_type(self) -> Type[ast.stmt]:
        if self == TransformType.CLASS:
            return ast.ClassDef
        if self == TransformType.FUNCTION:
            return ast.FunctionDef
        raise NotImplementedError(f"Unhandled transform type: {self}")
