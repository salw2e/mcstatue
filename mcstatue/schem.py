import gzip
import struct

import numpy as np

# 1.20.1, so WorldEdit on newer servers upgrades it
DATA_VERSION = 3465


def _name(b, name):
    raw = name.encode()
    b += struct.pack(">H", len(raw)) + raw


def _tag(b, kind, name, value):
    b.append(kind)
    _name(b, name)
    if kind == 2:
        b += struct.pack(">h", value)
    elif kind == 3:
        b += struct.pack(">i", value)
    elif kind == 7:
        b += struct.pack(">i", len(value)) + bytes(value)
    elif kind == 11:
        b += struct.pack(">i", len(value)) + struct.pack(f">{len(value)}i", *value)
    elif kind == 10:
        for k, v in value:
            _tag(b, *v[:1], k, v[1])
        b.append(0)


def _varints(values):
    out = bytearray()
    for v in values:
        while v >= 0x80:
            out.append(v & 0x7F | 0x80)
            v >>= 7
        out.append(v)
    return out


def write(path, grid, names):
    """grid is a (x, y, z) array of indexes into names, -1 for air"""
    w, h, l = grid.shape
    used = np.unique(grid[grid >= 0])
    remap = np.zeros(len(names) + 1, dtype=np.int64)
    remap[used + 1] = np.arange(1, len(used) + 1)
    blocks = ["minecraft:air"] + [f"minecraft:{names[i]}" for i in used]
    order = remap[grid.transpose(1, 2, 0).reshape(-1) + 1]  # index = x + z*w + y*w*l
    b = bytearray()
    _tag(b, 10, "Schematic", [
        ("Version", (3, 2)),
        ("DataVersion", (3, DATA_VERSION)),
        ("Width", (2, w)),
        ("Height", (2, h)),
        ("Length", (2, l)),
        ("Offset", (11, [0, 0, 0])),
        ("PaletteMax", (3, len(blocks))),
        ("Palette", (10, [(n, (3, i)) for i, n in enumerate(blocks)])),
        ("BlockData", (7, _varints(order.astype(np.int64).tolist()))),
    ])
    with gzip.open(path, "wb") as f:
        f.write(bytes(b))
