import glob
import os


def is_python_file(filename: str) -> bool:
    """Return True if a file appears to contain Python source code."""
    return filename.endswith(".py") or filename.endswith(".pyi")


def collect_python_files(targets: list[str]) -> list[str]:
    """Enumerate all Python files in a target."""
    collected: set[str] = set()
    for target in targets:
        for file_or_directory in glob.iglob(target):
            if os.path.isdir(file_or_directory):
                for root, dirnames, filenames in os.walk(file_or_directory):
                    for filename in filenames:
                        if is_python_file(filename):
                            collected.add(os.path.join(root, filename))
            elif os.path.isfile(file_or_directory):
                if is_python_file(file_or_directory):
                    collected.add(file_or_directory)

    return sorted(collected)
