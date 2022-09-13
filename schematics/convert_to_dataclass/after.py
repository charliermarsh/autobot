@dataclass
class MyClass:
    x: int
    y: int
    z: int

    def __post_init__(self) -> None:
        print("Initialized MyClass!")
