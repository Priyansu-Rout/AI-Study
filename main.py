"""
create_structure.py

Reads a tree-style file listing (like the one you saved as structure.txt,
using ├──, └──, │ characters) and creates all the folders and files on disk.

USAGE:
    1. Put this script in the same folder as structure.txt
       (or edit STRUCTURE_FILE below to point to it).
    2. Run:
         python create_structure.py
    3. It will create everything inside ./AI-Study/  (or whatever your
       root folder in structure.txt is named).
"""

import os
import re

STRUCTURE_FILE = "structure.txt"   # path to your saved tree file
OUTPUT_ROOT = "."                   # where to create the structure (current folder)


def clean_line(line: str) -> str:
    """Remove tree-drawing characters (│, ├──, └──, spaces) and comments."""
    # strip inline comments like "  # git submodule ..."
    line = re.split(r"\s+#", line)[0]
    # remove tree characters
    line = line.replace("│", "")
    line = re.sub(r"[├└]──\s?", "", line)
    return line.rstrip("\n")


def get_depth(raw_line: str) -> int:
    """
    Figure out nesting depth by counting groups of 4 characters
    (│ spacing or blank spacing) before the ├── / └── marker.
    """
    match = re.search(r"[├└]──", raw_line)
    prefix = raw_line[:match.start()] if match else raw_line
    # each nesting level in the tree uses 4 characters of prefix
    return len(prefix) // 4


def parse_structure(filepath):
    """Yield (depth, name, is_dir) tuples for each line in the tree file."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entries = []
    root_name = None

    for raw in lines:
        if not raw.strip():
            continue
        if raw.strip().startswith("```"):
            continue  # skip markdown code-fence lines if present

        stripped = raw.rstrip("\n")

        # Root line has no tree characters and ends with "/"
        if root_name is None and re.match(r"^[A-Za-z0-9_.\-]+/?\s*$", stripped.strip()):
            root_name = stripped.strip().rstrip("/")
            continue

        if "├──" not in raw and "└──" not in raw:
            continue

        depth = get_depth(raw)
        name = clean_line(raw).strip()
        if not name:
            continue

        is_dir = name.endswith("/")
        name = name.rstrip("/")
        entries.append((depth, name, is_dir))

    return root_name, entries


def build_structure(root_name, entries, output_root="."):
    root_path = os.path.join(output_root, root_name) if root_name else output_root
    os.makedirs(root_path, exist_ok=True)

    # stack holds the current path for each depth level
    stack = {0: root_path}

    for depth, name, is_dir in entries:
        parent_path = stack.get(depth, root_path)
        full_path = os.path.join(parent_path, name)

        if is_dir:
            os.makedirs(full_path, exist_ok=True)
            stack[depth + 1] = full_path
            print(f"[DIR ] {full_path}")
        else:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            if not os.path.exists(full_path):
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write("")
            print(f"[FILE] {full_path}")


if __name__ == "__main__":
    if not os.path.exists(STRUCTURE_FILE):
        print(f"Could not find '{STRUCTURE_FILE}'. Put it next to this script, "
              f"or edit STRUCTURE_FILE at the top of the script.")
        raise SystemExit(1)

    root, entries = parse_structure(STRUCTURE_FILE)
    if not entries:
        print("No entries found — check that structure.txt uses the "
              "├──/└──/│ tree format.")
        raise SystemExit(1)

    build_structure(root, entries, OUTPUT_ROOT)
    print(f"\nDone! Structure created under: {os.path.join(OUTPUT_ROOT, root or '')}")