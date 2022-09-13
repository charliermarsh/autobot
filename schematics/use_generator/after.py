def compute_squares(n: int) -> Generator[int, None, None]:
    for i in range(n):
        yield i * i
