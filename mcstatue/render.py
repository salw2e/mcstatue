import itertools
import math

import numpy as np
from PIL import Image, ImageDraw

from .blocks import COLORS

SHADE = {"top": 1.0, "x": 0.72, "z": 0.86}


def preview(grid, names, path, size=1200, turn=30, tilt=30):
    """picture of the statue, camera mostly in front (+z), turned towards +x and looking down"""
    w, h, l = grid.shape
    solid = grid >= 0
    t, p = math.radians(turn), math.radians(tilt)
    right = np.array([math.cos(t), 0, -math.sin(t)])
    up = np.array([-math.sin(t) * math.sin(p), math.cos(p), -math.cos(t) * math.sin(p)])
    toward = np.array([math.sin(t) * math.cos(p), math.sin(p), math.cos(t) * math.cos(p)])

    corners = np.array(list(itertools.product((0, w), (0, h), (0, l))))
    sx, sy = corners @ right, -(corners @ up)
    scale = size / max(np.ptp(sx), np.ptp(sy))
    ox, oy = -sx.min() * scale, -sy.min() * scale
    img = Image.new("RGBA", (int(np.ptp(sx) * scale) + 1, int(np.ptp(sy) * scale) + 1), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def px(x, y, z):
        v = np.array([x, y, z])
        return (v @ right * scale + ox, -(v @ up) * scale + oy)

    def open_(x, y, z):
        return not (0 <= x < w and 0 <= y < h and 0 <= z < l) or not solid[x, y, z]

    cells = np.argwhere(solid)
    cells = cells[np.argsort(cells @ toward, kind="stable")]
    for x, y, z in cells:
        rgb = np.array(COLORS[names[grid[x, y, z]]])
        faces = []
        if open_(x, y + 1, z):
            faces.append(("top", [(x, y + 1, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)]))
        if open_(x + 1, y, z):
            faces.append(("x", [(x + 1, y, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x + 1, y, z + 1)]))
        if open_(x, y, z + 1):
            faces.append(("z", [(x, y, z + 1), (x + 1, y, z + 1), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)]))
        for side, pts in faces:
            c = rgb * SHADE[side]
            d.polygon([px(*q) for q in pts], fill=tuple(int(v) for v in c) + (255,), outline=tuple(int(v) for v in c * 0.85) + (255,))
    box = img.getbbox()
    if box:
        pad = int(scale * 2)
        img = img.crop((box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad))
    img.save(path)
