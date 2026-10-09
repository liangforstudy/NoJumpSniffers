"""Set the add-on version. Usage: python3 tools/bump.py 1.1.0

UUIDs are NOT changed, so the new build installs as an update of the same pack.
"""
import json
import re
import sys
from pathlib import Path

if len(sys.argv) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", sys.argv[1]):
    sys.exit("usage: python3 tools/bump.py MAJOR.MINOR.PATCH")

v = [int(x) for x in sys.argv[1].split(".")]
path = Path(__file__).resolve().parent.parent / "packs/BP/manifest.json"
m = json.loads(path.read_text())
m["header"]["version"] = v
for mod in m["modules"]:
    mod["version"] = v
m["metadata"] = {"product_type": "addon"}
path.write_text(json.dumps(m, indent=2))
print("version set to", sys.argv[1])
