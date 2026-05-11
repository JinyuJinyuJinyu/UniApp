"""cli_view.py

Student Name: Sai Som Seng
Student ID: 25724218
"""

# Small helpers for printing/prompting in the CLI so the controllers
# don't have to deal with raw print() and input() calls.


def banner(title):
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


def divider():
    print("─" * 60)


def prompt(text):
    return input(f"  {text}: ").strip()


# Tiny wrappers for the four message types we use.

def info(msg):
    print(f"  ✔  {msg}")

def warn(msg):
    print(f"  ⚠  {msg}")

def error(msg):
    print(f"  ✘  {msg}")

def success(msg):
    print(f"  ✔  {msg}")
