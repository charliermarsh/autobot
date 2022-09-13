class MemoryCacheTest(unittest.TestCase):
    def test_roundtrip(self) -> None:
        cache = MemoryCache(scope="test_roundtrip")

        expected = uuid.uuid4().hex.encode("utf-8")
        cache.set("VALUE", io.BytesIO(expected))
        actual = cache.get("VALUE") or io.BytesIO()

        self.assertEqual(expected, actual.getvalue())
