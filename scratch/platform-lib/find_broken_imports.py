"""
find_broken_imports.py

Run this from inside the platform-lib folder (where src/ lives):
    python find_broken_imports.py

What it does (simple explanation):
- Walks through every single .py file inside src/hogc
- Tries to import each one
- Prints a clean list of what's broken and why
- At the end, prints a summary count

This does NOT fix anything. It just finds every problem in one go,
instead of you discovering them one crash at a time.
"""
import importlib
import pathlib
import sys
import traceback

# Make sure src/ is on the path so "hogc..." imports work
ROOT = pathlib.Path(__file__).parent.resolve()
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

PACKAGE_ROOT = SRC / "hogc"

broken = []
ok_count = 0

for py_file in sorted(PACKAGE_ROOT.rglob("*.py")):
    if "__pycache__" in str(py_file):
        continue

    # Convert file path to a dotted module name
    # e.g. src/hogc/lib/kernel/errors.py -> hogc.lib.kernel.errors
    rel_path = py_file.relative_to(SRC)
    if rel_path.name == "__init__.py":
        module_name = ".".join(rel_path.parts[:-1])
    else:
        module_name = ".".join(rel_path.with_suffix("").parts)

    if not module_name:
        continue

    try:
        importlib.import_module(module_name)
        ok_count += 1
    except Exception as e:
        broken.append((module_name, str(py_file), f"{type(e).__name__}: {e}"))

print("=" * 70)
print(f"CHECKED: {ok_count + len(broken)} modules")
print(f"OK:      {ok_count}")
print(f"BROKEN:  {len(broken)}")
print("=" * 70)

if broken:
    print("\nBROKEN MODULES:\n")
    for module_name, file_path, error in broken:
        print(f"- {module_name}")
        print(f"    file:  {file_path}")
        print(f"    error: {error}")
        print()
else:
    print("\nEverything imported successfully!")