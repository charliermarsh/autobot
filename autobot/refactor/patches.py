import os
import subprocess

PATCH_DIR = os.path.join(os.getcwd(), ".autobot_patches")


def save(patch: str, *, target: str, lineno: int) -> None:
    """Save a patch to disk."""
    (target_filename, _) = os.path.splitext(target)
    patch_filename = os.path.join(
        PATCH_DIR,
        f"{target_filename}-{lineno}.patch",
    )
    os.makedirs(os.path.dirname(patch_filename), exist_ok=True)
    with open(patch_filename, "w") as fp:
        fp.write(patch)


def can_apply(patch_file: str) -> bool:
    """Return True if a patch file can be applied to its target."""
    result = subprocess.run(
        ["git", "apply", "--check", patch_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def apply(patch_file: str) -> None:
    """Apply a patch file to its target."""
    subprocess.check_call(["git", "apply", patch_file])
