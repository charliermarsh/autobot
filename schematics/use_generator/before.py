def compute_squares(n: int) -> list[int]:
    squares: list[int] = []
    for i in range(n):
        squares.append(i * i)
    return squares
