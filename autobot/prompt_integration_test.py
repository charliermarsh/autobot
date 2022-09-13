"""Test cases to assess prompt completion.

Note that these tests rely on the OpenAI API.
"""
import unittest

from dotenv import load_dotenv

from autobot import api, prompt
from autobot.transforms import TransformType


class PromptIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv()
        api.init()

    def test_useless_object_inheritance(self) -> None:
        before_text = """
class Foo(Bar, object):
    def __init__(self, x: int) -> None:
        self.x = x
"""

        after_text = """
class Foo(Bar):
    def __init__(self, x: int) -> None:
        self.x = x
"""

        snippet = """
class CreateTaskResponse(object):
    task_id: str
        """

        expected = """
class CreateTaskResponse:
    task_id: str
        """
        actual = prompt.resolve_prompt(
            prompt.make_prompt(
                snippet.strip(),
                transform_type=TransformType.CLASS,
                before_text=before_text.strip(),
                after_text=after_text.strip(),
                before_description="with object inheritance",
                after_description="without object inheritance",
            )
        )

        self.assertEqual(expected.strip(), actual.strip())

    def test_sorted_attributes(self) -> None:
        before_text = """
class MyUnsortedConstants:
    z = "hehehe"
    B = "aaa234"
    A = "zzz123"
    cab = "foo bar"
    Daaa = "banana"
"""

        after_text = """
class MyUnsortedConstants:
    A = "zzz123"
    B = "aaa234"
    Daaa = "banana"
    cab = "foo bar"
    z = "hehehe"
"""

        snippet = """
@dataclass
class Circle:
    \"\"\"A circle in an image, with all its pixel indices/radius/center.\"\"\"

    # All the row coordinates of pixels in the circle, suitable for logical
    # indexing with numpy.
    rr: np.ndarray

    # All the column coordinates of pixels in the circle, suitable for logical
    # indexing with numpy.
    cc: np.ndarray

    # Radius of the circle
    radius: int

    # Center of the circle (row, column)
    center: Tuple[int, int]
"""

        expected = """
@dataclass
class Circle:
    \"\"\"A circle in an image, with all its pixel indices/radius/center.\"\"\"

    # All the column coordinates of pixels in the circle, suitable for logical
    # indexing with numpy.
    cc: np.ndarray

    # Center of the circle (row, column)
    center: Tuple[int, int]

    # Radius of the circle
    radius: int

    # All the row coordinates of pixels in the circle, suitable for logical
    # indexing with numpy.
    rr: np.ndarray
"""
        actual = prompt.resolve_prompt(
            prompt.make_prompt(
                snippet.strip(),
                transform_type=TransformType.CLASS,
                before_text=before_text.strip(),
                after_text=after_text.strip(),
                before_description="with unsorted class attributes",
                after_description="with alphabetically sorted class attributes",
            )
        )

        self.assertEqual(expected.strip(), actual.strip())

    def test_standard_library_generics(self) -> None:
        before_text = """
def func(
    x: Optional[List[int]],
    y: Optional[int],
    z: Optional[Union[int, List[int]]],
) -> None:
    a: List[int] = []
    b: Set[int] = set()
    c: Optional[int] = 0
    d: Union[int, str] = 0
"""

        after_text = """
def func(
    x: list[int] | None,
    y: int | None,
    z: int | list[int] | None,
) -> None:
    a: list[int] = []
    b: set[int] = set()
    c: int | None = 0
    d: int | str = 0
"""

        snippet = """
def compute_squares(n: int) -> List[int]:
    x: List[int] = []
    for i in range(n):
        x.append(i * i)
    return x
"""

        expected = """
def compute_squares(n: int) -> list[int]:
    x: list[int] = []
    for i in range(n):
        x.append(i * i)
    return x
"""
        actual = prompt.resolve_prompt(
            prompt.make_prompt(
                snippet.strip(),
                transform_type=TransformType.CLASS,
                before_text=before_text.strip(),
                after_text=after_text.strip(),
                before_description="with typing module generics",
                after_description="with standard library generics",
            )
        )

        self.assertEqual(expected.strip(), actual.strip())

    def test_use_generator(self) -> None:
        before_text = """
def compute_squares(n: int) -> list[int]:
    squares: list[int] = []
    for i in range(n):
        squares.append(i * i)
    return squares
    """

        after_text = """
def compute_squares(n: int) -> Generator[int, None, None]:
    for i in range(n):
        yield i * i
    """

        snippet = """
def run(self, parameter_name: str, value: pd.DataFrame) -> list[SpecViolation]:
    violations: list[SpecViolation] = []
    cols = value.columns if isinstance(self.columns, _All) else self.columns
    for col in cols:
        if col not in value.columns:
            violations.append(
                SpecViolation(
                    parameter_name,
                    f"column {col} missing from dataframe",
                    pd.DataFrame,
                    value,
                )
            )
        elif value[col].isnull().values.any():
            violations.append(
                SpecViolation(
                    parameter_name,
                    f"column {col} had null values",
                    pd.DataFrame,
                    value,
                )
            )
    return violations
            """

        expected = """
def run(self, parameter_name: str, value: pd.DataFrame) -> Generator[SpecViolation, None, None]:
    cols = value.columns if isinstance(self.columns, _All) else self.columns
    for col in cols:
        if col not in value.columns:
            yield SpecViolation(
                parameter_name,
                f"column {col} missing from dataframe",
                pd.DataFrame,
                value,
            )
        elif value[col].isnull().values.any():
            yield SpecViolation(
                parameter_name,
                f"column {col} had null values",
                pd.DataFrame,
                value,
            )
            """

        actual = prompt.resolve_prompt(
            prompt.make_prompt(
                snippet.strip(),
                transform_type=TransformType.FUNCTION,
                before_text=before_text.strip(),
                after_text=after_text.strip(),
                before_description="as a list builder",
                after_description="as a generator",
            )
        )

        self.assertEqual(expected.strip(), actual.strip())
