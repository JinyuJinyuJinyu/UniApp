"""
cli_view.py – CLI presentation helpers (View layer)
====================================================
All terminal output — banners, dividers, prompts, status lines — is
funnelled through this module. Controllers import these helpers so the
business logic never touches print() / input() directly.
"""

import os


# ── chrome ────────────────────────────────────────────────────────────────────

def clear() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def banner(title: str) -> None:
    """Print a section banner."""
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


def divider() -> None:
    """Print a horizontal divider."""
    print("─" * 60)


# ── input ─────────────────────────────────────────────────────────────────────

def prompt(text: str) -> str:
    """Read a line of input with a 'text:' label."""
    return input(f"  {text}: ").strip()


# ── status lines ──────────────────────────────────────────────────────────────

def info(msg: str)    -> None: print(f"  ✔  {msg}")
def warn(msg: str)    -> None: print(f"  ⚠  {msg}")
def error(msg: str)   -> None: print(f"  ✘  {msg}")
def success(msg: str) -> None: print(f"  ✔  {msg}")
