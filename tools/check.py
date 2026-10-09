"""Sanity checks run by build.sh before packaging."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "packs"
errors = []


def load(rel):
    try:
        data = json.loads((P / rel).read_text())
        print(f"ok   {rel}")
        return data
    except Exception as e:  # noqa: BLE001
        errors.append(f"{rel}: invalid JSON ({e})")
        return None


bp = load("BP/manifest.json")
ent = load("BP/entities/sniffer.json")

if (P / "RP").exists():
    errors.append("this add-on is behavior-pack only; packs/RP should not exist")
if (P / "BP/scripts").exists() or (P / "BP/entities/parrot.json").exists():
    errors.append("parrot / script files found; this pack must not contain Parrot Party Range content")

if bp:
    for mod in bp["modules"]:
        if mod["version"] != bp["header"]["version"]:
            errors.append(f"module {mod['type']} version {mod['version']} != header")
    if bp.get("metadata", {}).get("product_type") != "addon":
        errors.append('manifest missing "metadata": { "product_type": "addon" }')
    parrot_uuids = {"6b74ffdd-dd58-4e57-8c71-2f86e45a1caa", "f4f6d874-764b-418e-9da9-9e11d65434e6"}
    if bp["header"]["uuid"] in parrot_uuids:
        errors.append("manifest reuses a Parrot Party Range uuid")

if ent:
    e = ent["minecraft:entity"]
    c = e["components"]
    if e["description"]["identifier"] != "minecraft:sniffer":
        errors.append("entity identifier must be minecraft:sniffer")
    g = e.get("component_groups", {})
    land = g.get("nj:land", {})
    if land.get("minecraft:jump.static", {}).get("jump_power") != 0:
        errors.append("nj:land jump_power should be 0")
    if land.get("minecraft:navigation.walk", {}).get("can_jump") is not False:
        errors.append("nj:land navigation.walk can_jump should be false")
    if land.get("minecraft:variable_max_auto_step", {}).get("base_value", 1) >= 0.5:
        errors.append("nj:land auto step must be below 0.5 so slabs block them")
    swapped = ("minecraft:jump.static", "minecraft:navigation.walk", "minecraft:variable_max_auto_step")
    for key in swapped:
        if key in c:
            errors.append(f"{key} must not be in base components (removing a group would delete it)")
        for gname in ("nj:land", "nj:water"):
            if key not in g.get(gname, {}):
                errors.append(f"{gname} missing {key}")
    # Keep the parts that made the user's own attempt freeze the sniffers intact.
    for key in ("minecraft:movement", "minecraft:movement.basic", "minecraft:behavior.random_stroll",
                "minecraft:behavior.float"):
        if key not in c:
            errors.append(f"{key} is missing (sniffers would stop moving / sink)")
    # Every group referenced by an event must exist.
    groups = set(e.get("component_groups", {}))
    for name, ev in e.get("events", {}).items():
        for part in [ev] + ev.get("sequence", []):
            for op in ("add", "remove"):
                for g in part.get(op, {}).get("component_groups", []):
                    if g not in groups:
                        errors.append(f"event {name} references missing group {g}")

if errors:
    print("\nFAILED:")
    for x in errors:
        print("  -", x)
    sys.exit(1)
print("ok   all checks passed")
