import numpy as np
from scipy import ndimage

from .blocks import nearest


def blocks(density, color, names, s=2, threshold=25.0, solid=False):
    """density and color sampled s times per block edge -> (x, y, z) grid of palette indexes, -1 is air"""
    w, h, l = (n // s for n in density.shape)
    density = density.reshape(w, s, h, s, l, s)
    color = color.reshape(w, s, h, s, l, s, 3)
    inside = (density > threshold).mean(axis=(1, 3, 5)) >= 0.5
    inside = ndimage.binary_fill_holes(inside)
    # keep the biggest piece, the model leaves specks floating around it
    labels, count = ndimage.label(inside)
    if count > 1:
        sizes = ndimage.sum(inside, labels, range(1, count + 1))
        inside = labels == sizes.argmax() + 1
    if not solid:
        inside &= ~ndimage.binary_erosion(inside, border_value=0)

    # colour of a block = average of its samples near the surface
    surf = density > threshold
    weight = surf[..., None]
    rgb = (color * weight).sum(axis=(1, 3, 5)) / np.maximum(weight.sum(axis=(1, 3, 5)), 1)
    plain = color.mean(axis=(1, 3, 5))
    rgb = np.where(weight.sum(axis=(1, 3, 5)) > 0, rgb, plain)

    grid = np.full(inside.shape, -1, dtype=np.int32)
    cells = np.argwhere(inside)
    grid[tuple(cells.T)] = nearest(np.clip(rgb[tuple(cells.T)], 0, 1) * 255, names)
    return grid
