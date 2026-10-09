# No Jump Sniffers - handoff

Minecraft Bedrock add-on (behavior pack only) that stops sniffers and
snifflets from jumping or stepping up any block on land, including slabs and
stairs. They still float in water, and while in water they get their vanilla
jump back so they can climb out of the pond. Built for Bedrock v26.52, used
on a Realm, next to their separate Parrot Party Range add-on.
Current version: **1.0.0** (not yet tested in game).

This is a separate add-on from Parrot Party Range on purpose: each can be
turned on or off by itself. It must never contain any parrot files, scripts
or Parrot Party Range UUIDs (check.py enforces this).

## Quick start for the next chat

1. Unzip `NoJumpSniffers-source.zip` into a fresh folder.
2. Tools: `python3` (standard library), `zip`, `unzip`. Nothing is compiled.
3. `chmod +x build.sh && ./build.sh` -> `dist/NoJumpSniffers_v<version>.mcaddon`.
4. To release a change: edit `tools/regen_sniffer.py` (not the generated
   entity file), run `python3 tools/regen_sniffer.py`, then
   `python3 tools/bump.py 1.1.0`, then `./build.sh`.

## Layout

```
build.sh                        validate + zip into dist/*.mcaddon
tools/regen_sniffer.py          makes packs/BP/entities/sniffer.json from vanilla (all the logic)
tools/check.py                  checks run by build.sh
tools/bump.py                   set version (UUIDs stay the same)
vanilla/sniffer.json            Mojang's vanilla sniffer (bedrock-samples, format 1.26.10)
packs/BP/manifest.json
packs/BP/entities/sniffer.json  generated override of minecraft:sniffer
packs/BP/pack_icon.png
```

## How it works

- `jump.static`, `navigation.walk` and `variable_max_auto_step` are removed
  from the base components and live only in two component groups:
  - `nj:land`: jump_power 0, navigation `can_jump: false`, auto step 0.125
    (blocks slabs/stairs, still lets them over carpet, snow layers, path lips).
  - `nj:water`: vanilla values (jump on, step 0.5625) so they can get out.
- An `environment_sensor` swaps the groups using the `in_water` filter. An
  enum property `nj:state` (none/land/water, default none) makes it fire only
  on a change, and makes existing sniffers pick up `nj:land` on their first tick.
- Floating is vanilla `behavior.float`, untouched.
- Babies use the same base components, so the rule covers them too.

## Rules (learned the hard way)

- **Never override a base component inside a group that later gets removed.**
  Removing a group deletes its components from the mob even if the base
  components have them. That's how sniffers become statues (they lose
  navigation). That's why the three components are only in the swapped groups.
- Keep `"metadata": { "product_type": "addon" }` in the manifest (keeps achievements on).
- Namespace is `nj:`. Never put the user's name or handles anywhere in the pack.
- Keep the UUIDs between releases and just raise the version.
- To make it strict (no water exception), set `WATER_EXIT = False` in
  regen_sniffer.py. A sniffer in the pond would then float there forever.

## Things to confirm in game (untested)

- Sniffers walk around normally on flat ground (not statues).
- They can't get onto a 1-block step, a slab or stairs.
- Falling into the pond: they float and can climb back out.
- If they get stuck at the pond edge or something odd happens, turn on
  Settings > Creator > Enable Content Log GUI and get a screenshot.

## Updating on the user's side

Same as Parrot Party Range: remove the old version from the world, load in
once without it, exit, add the new version, then check Technical details.

## Publishing

GitHub repo: github.com/liangforstudy/NoJumpSniffers. After `./build.sh`, commit
`download/NoJumpSniffers.mcaddon` (build.sh copies it there). The README download link
points at that file on main, so it always serves the latest build.
