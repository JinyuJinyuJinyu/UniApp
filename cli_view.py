"""cli_view.py 

Student Name: Sai Som Seng
Student ID: 25724218"""

"""
cli_view.py - CLI presentation helpers (View layer)
====================================================
All terminal output — banners, dividers, prompts, status lines — is
funnelled through this module. Controllers import these helpers so the
business logic never touches print() / input() directly.
"""

# ═════════════════════════════════════════════════════════════════════════
#  Terminal Display
# ═════════════════════════════════════════════════════════════════════════

#Print a section banner
def banner(title):
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)

#Horizontal Divider
def divider():
    print("─" * 60)


# ═════════════════════════════════════════════════════════════════════════
#  Input
# ═════════════════════════════════════════════════════════════════════════

def prompt(text):
    return input(f"  {text}: ").strip()

# ═════════════════════════════════════════════════════════════════════════
#  Message
# ═════════════════════════════════════════════════════════════════════════

def info(msg): 
    print(f"  ✔  {msg}")

def warn(msg): 
    print(f"  ⚠  {msg}")

def error(msg): 
    print(f"  ✘  {msg}")

def success(msg): 
    print(f"  ✔  {msg}")
