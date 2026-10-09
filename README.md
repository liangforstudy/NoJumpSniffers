# No Jump Sniffers

A Minecraft Bedrock add-on that stops sniffers from jumping.

**[Download NoJumpSniffers.mcaddon](https://github.com/liangforstudy/NoJumpSniffers/raw/main/download/NoJumpSniffers.mcaddon)**

## What it does

- Sniffers and baby sniffers can't jump on land.
- They can't climb any block either, including slabs and stairs. Thin things like carpet and snow layers are still fine.
- In water they float like normal, so they won't drown. They can also jump while in water, so one that falls in can climb back out.
- Everything else (sniffing, digging up seeds, breeding) is vanilla.

It only changes sniffers. It's a behavior pack only, with no scripts and no resource pack, and it works alongside other add-ons that don't change sniffers.

## Install

1. Tap the download link above and open the file with Minecraft.
2. In your world or Realm settings, go to **Behavior Packs** and activate **No Jump Sniffers**.

Built for Minecraft Bedrock 26.x.

## Building from source

Needs `python3` and `zip`. Run `./build.sh` and the add-on is written to `dist/`. See `HANDOFF.md` for how it works.
