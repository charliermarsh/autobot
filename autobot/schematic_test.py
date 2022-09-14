import os.path
import unittest

from autobot.schematic import Schematic
from autobot.transforms import TransformType


class SchematicTest(unittest.TestCase):
    def test_from_directory__class(self) -> None:
        expected = Schematic(
            title="assert_equals",
            before_text="""class MemoryCacheTest(unittest.TestCase):
    def test_roundtrip(self) -> None:
        cache = MemoryCache(scope="test_roundtrip")

        expected = uuid.uuid4().hex.encode("utf-8")
        cache.set("VALUE", io.BytesIO(expected))
        actual = cache.get("VALUE") or io.BytesIO()

        self.assertEquals(expected, actual.getvalue())""",
            after_text="""class MemoryCacheTest(unittest.TestCase):
    def test_roundtrip(self) -> None:
        cache = MemoryCache(scope="test_roundtrip")

        expected = uuid.uuid4().hex.encode("utf-8")
        cache.set("VALUE", io.BytesIO(expected))
        actual = cache.get("VALUE") or io.BytesIO()

        self.assertEqual(expected, actual.getvalue())""",
            before_description="with self.assertEquals",
            after_description="without self.assertEquals",
            transform_type=TransformType.CLASS,
        )
        actual = Schematic.from_directory(
            os.path.join(
                os.path.dirname(__file__),
                "schematics",
                "assert_equals",
            )
        )

        self.assertEqual(expected, actual)

    def test_from_directory__function(self) -> None:
        expected = Schematic(
            title="numpy_builtin_aliases",
            before_text="""def f() -> None:
    a = np.array(dtype=np.int)
    b = np.dtype(np.unicode)
    c = np.dtype(np.object)
    d = np.float(123)""",
            after_text="""def f() -> None:
    a = np.array(dtype=int)
    b = np.dtype(str)
    c = np.dtype(object)
    d = float(123)""",
            before_description="with NumPy's builtin aliases (like np.int)",
            after_description=(
                "without NumPy's deprecated aliases (so int instead of np.int)"
            ),
            transform_type=TransformType.FUNCTION,
        )
        actual = Schematic.from_directory(
            os.path.join(
                os.path.dirname(__file__),
                "schematics",
                "numpy_builtin_aliases",
            )
        )

        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
