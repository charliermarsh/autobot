import enum
import os
from typing import Dict, List, Optional

from colorama import Fore
from rich.console import Console

from autobot.constants import PATCH_DIR
from autobot.refactor import patch
from autobot.utils.getch import getch


class Resolution(enum.Enum):
    ACCEPT = "a"
    REJECT = "r"
    SKIP = "s"

    @classmethod
    def from_code(cls, code: str) -> Optional["Resolution"]:
        try:
            return cls(code)
        except ValueError:
            return None


def run_review() -> None:
    patches: List[str] = []
    for root, _, filenames in os.walk(PATCH_DIR):
        for filename in filenames:
            if filename.endswith(".patch"):
                patches.append(os.path.join(root, filename))

    console = Console()

    patches_by_resolution: Dict[Resolution, List[str]] = {
        Resolution.ACCEPT: [],
        Resolution.REJECT: [],
        Resolution.SKIP: [],
    }
    num_patches = len(patches)
    for i, patch_file in enumerate(patches):
        if patch.can_apply(patch_file):
            with console.screen(hide_cursor=False):
                with open(patch_file, "r") as fp:
                    contents = fp.read()

                console.print(
                    f"[bold][white]Reviewing [[yellow]{i + 1}/{num_patches}[/yellow]]"
                )
                console.print(f"Patch file: [cyan]{os.path.basename(patch_file)}")

                console.print()
                for line in contents.splitlines():
                    stripped = line.strip()
                    if len(stripped) == 0:
                        line = stripped
                    if line.startswith("-"):
                        print(f"{Fore.RED}{line}{Fore.RESET}")
                    elif line.startswith("+"):
                        print(f"{Fore.GREEN}{line}{Fore.RESET}")
                    else:
                        print(line)
                console.print()

                console.print("  [bold green]a[/] accept  [grey46]apply the patch[/]")
                console.print("  [bold red]r[/] reject  [grey46]reject the patch[/]")
                console.print("  [bold yellow]s[/] skip    [grey46]skip the patch[/]")

                try:
                    while (resolution := Resolution(getch())) is None:
                        pass
                except KeyboardInterrupt:
                    exit(0)

                patches_by_resolution[resolution].append(patch_file)
                if resolution == Resolution.ACCEPT:
                    # Apply the patch.
                    patch.apply(patch_file)
                    os.remove(patch_file)
                elif resolution == Resolution.REJECT:
                    # Reject the patch.
                    os.remove(patch_file)
                elif resolution == Resolution.SKIP:
                    # Do nothing.
                    pass
                else:
                    raise ValueError(f"Unexpected resolution: {resolution}")

    if num_patches > 0:
        if num_patches == 1:
            console.print(f"[bold]Done![/] Reviewed {len(patches)} patch.")
        else:
            console.print(f"[bold]Done![/] Reviewed {len(patches)} patches.")
        for resolution in patches_by_resolution:
            if patches_by_resolution[resolution]:
                if resolution == Resolution.ACCEPT:
                    console.print("[green]Accepted:")
                elif resolution == Resolution.REJECT:
                    console.print("[red]Rejected:")
                elif resolution == Resolution.SKIP:
                    console.print("[yellow]Skipped:")
                else:
                    raise ValueError(f"Unexpected resolution: {resolution}")

                for patch_file in patches_by_resolution[resolution]:
                    print(f"  {os.path.relpath(patch_file, PATCH_DIR)}")
    else:
        console.print("[bold]Done![/] No patches to review.")
