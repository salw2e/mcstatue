import numpy as np
from PIL import Image, ImageDraw

from .blocks import COLORS

SHADE = {"top": 1.0, "x": 0.8, "z": 0.62}


def preview(grid, names, path, size=1200):
    """isometric picture of the statue, seen from the +x +z corner"""
    w, h, l = grid.shape
    solid = grid >= 0
    a = 2 * size / ((w + l) * 0.866 * 2 + h)
    px = lambda x, y, z: ((x - z) * a * 0.866, (x + z) * a * 0.5 - y * a)
    xs, ys = zip(px(0, 0, l), px(w, 0, 0), px(0, h, 0), px(w, 0, l))
    ox, oy = -min(xs) + a, -min(ys) + a
    img = Image.new("RGBA", (int(max(xs) + ox + a), int(max(ys) + oy + a)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def open_(x, y, z):
        return not (0 <= x < w and 0 <= y < h and 0 <= z < l) or not solid[x, y, z]

    cells = np.argwhere(solid)
    cells = cells[np.argsort(cells.sum(1), kind="stable")]
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
            c = tuple(int(v) for v in rgb * SHADE[side]) + (255,)
            edge = tuple(int(v) for v in rgb * SHADE[side] * 0.82) + (255,)
            poly = [(px(*p)[0] + ox, px(*p)[1] + oy) for p in pts]
            d.polygon(poly, fill=c, outline=edge)
    box = img.getbbox()
    if box:
        pad = int(a * 2)
        img = img.crop((box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad))
    img.save(path)
