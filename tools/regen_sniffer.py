"""Build packs/BP/entities/sniffer.json from Mojang's vanilla sniffer.

Run this again if a Minecraft update changes the vanilla sniffer:
  1. curl -sfL https://raw.githubusercontent.com/Mojang/bedrock-samples/main/behavior_pack/entities/sniffer.json -o vanilla/sniffer.json
  2. python3 tools/regen_sniffer.py
  3. ./build.sh

What it changes (everything else stays vanilla):
  On land (adults and babies):
    - jump power 0, so the sniffer can't jump
    - pathfinding told it can't jump, so it doesn't plan routes up blocks
    - auto step height lowered from 0.5625 to STEP_ON_LAND, so it can't
      walk up slabs, stairs or other half blocks either
  In water:
    - keeps vanilla floating (behavior.float), so it doesn't sink or drown
    - while touching water the vanilla jump/step values come back, so a
      sniffer that falls in the pond can climb back out. Set
      WATER_EXIT = False for the strict version (it would float forever).
  Jump, pathfinding and step live in two swapped groups (nj:land / nj:water),
  never in the base components; see the comment below for why.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "vanilla" / "sniffer.json"
OUT = ROOT / "packs" / "BP" / "entities" / "sniffer.json"

# 0.125 = 2 pixels. Low enough to block slabs (0.5) and stairs, high enough
# that carpets, snow layers and the lip of dirt paths/farmland don't trap them.
STEP_ON_LAND = 0.125
VANILLA_STEP = 0.5625
WATER_EXIT = True

ent = json.loads(SRC.read_text())
e = ent["minecraft:entity"]
c = e["components"]

for key in ("minecraft:jump.static", "minecraft:navigation.walk", "minecraft:behavior.float"):
    if key not in c:
        raise SystemExit(f"vanilla sniffer no longer has {key}; check the file by hand")


def step(v):
    return {"base_value": v, "controlled_value": v, "jump_prevented_value": v}


# Bedrock gotcha: removing a component group deletes its components from the
# mob even if the base "components" also has them. So jump / pathfinding /
# step are taken OUT of the base components and live only in two groups that
# get swapped: nj:land and nj:water. A sniffer always has exactly one of them.
# (Overriding them in one group and removing it later = statue sniffers.)
nav = c.pop("minecraft:navigation.walk")
c.pop("minecraft:jump.static")

land = {
    "minecraft:jump.static": {"jump_power": 0.0},
    "minecraft:navigation.walk": dict(nav, can_jump=False),
    "minecraft:variable_max_auto_step": step(STEP_ON_LAND),
}
water = {
    "minecraft:jump.static": {},
    "minecraft:navigation.walk": dict(nav),
    "minecraft:variable_max_auto_step": step(VANILLA_STEP),
} if WATER_EXIT else land

for g in ("nj:land", "nj:water"):
    if g in e["component_groups"]:
        raise SystemExit(f"{g} already exists in vanilla sniffer?")
e["component_groups"]["nj:land"] = land
e["component_groups"]["nj:water"] = water

# Enum property remembers which group is on, so the sensor only fires when it
# needs to change (re-adding a group every tick would reset pathfinding).
# Default "none" means sniffers already in the world (and new spawns) get
# nj:land on their first tick.
e["description"].setdefault("properties", {})["nj:state"] = {
    "type": "enum", "values": ["none", "land", "water"], "default": "none"
}
e["events"]["nj:to_land"] = {
    "remove": {"component_groups": ["nj:water"]},
    "add": {"component_groups": ["nj:land"]},
    "set_property": {"nj:state": "land"},
}
e["events"]["nj:to_water"] = {
    "remove": {"component_groups": ["nj:land"]},
    "add": {"component_groups": ["nj:water"]},
    "set_property": {"nj:state": "water"},
}
if "minecraft:environment_sensor" in c:
    raise SystemExit("vanilla sniffer now has its own environment_sensor; merge triggers by hand")
c["minecraft:environment_sensor"] = {
    "triggers": [
        {
            "filters": {"all_of": [
                {"test": "in_water", "subject": "self", "value": True},
                {"test": "enum_property", "subject": "self", "domain": "nj:state",
                 "operator": "!=", "value": "water"},
            ]},
            "event": "nj:to_water",
        },
        {
            "filters": {"all_of": [
                {"test": "in_water", "subject": "self", "value": False},
                {"test": "enum_property", "subject": "self", "domain": "nj:state",
                 "operator": "!=", "value": "land"},
            ]},
            "event": "nj:to_land",
        },
    ]
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(ent, indent=2))
print("regenerated", OUT.relative_to(ROOT))
