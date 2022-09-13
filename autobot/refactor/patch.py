import subprocess


def can_apply(patch_file: str) -> bool:
    result = subprocess.run(
        ["git", "apply", "--check", patch_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def apply(patch_file: str) -> None:
    subprocess.check_call(["git", "apply", patch_file])
