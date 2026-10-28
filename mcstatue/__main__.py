import argparse
import collections
import os
import time

from . import blocks, render, schem, voxel


def main():
    p = argparse.ArgumentParser(prog="mcstatue", description="Turns a photo into a Minecraft statue (.schem)")
    p.add_argument("photo")
    p.add_argument("-o", "--out", help="output .schem, default is next to the photo")
    p.add_argument("--height", type=int, default=48, help="statue height in blocks (default 48)")
    p.add_argument("--blocks", default="all", help="all, wool, concrete, terracotta, or a list like white_wool,stone")
    p.add_argument("--solid", action="store_true", help="fill the inside instead of a one block shell")
    p.add_argument("--threads", type=int, help="CPU threads for the model")
    a = p.parse_args()

    names = blocks.palette(a.blocks)
    out = a.out or os.path.splitext(a.photo)[0] + ".schem"

    from . import model

    t = time.time()
    m = model.load(a.threads)
    image = model.cutout(a.photo)
    density, color = model.sample(m, image, a.height)
    grid = voxel.blocks(density, color, names, solid=a.solid)
    schem.write(out, grid, names)
    preview = os.path.splitext(out)[0] + ".png"
    render.preview(grid, names, preview)

    w, h, l = grid.shape
    used = collections.Counter(names[i] for i in grid[grid >= 0])
    print(f"{out}  {w}x{h}x{l}, {sum(used.values())} blocks, {time.time() - t:.0f}s")
    print(f"{preview}")
    for name, count in used.most_common(8):
        print(f"  {count:6d}  {name}")
    if len(used) > 8:
        print(f"  and {len(used) - 8} more")


if __name__ == "__main__":
    main()
