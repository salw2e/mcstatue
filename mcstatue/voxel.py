import numpy as np
from scipy import ndimage

from .blocks import nearest_lab, to_lab


def blocks(density, color, names, photo=None, s=2, threshold=25.0, solid=False, smooth=0.7):
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
    shell = inside & ~ndimage.binary_erosion(inside, border_value=0)
    if not solid:
        inside = shell

    # colour of a block = average of its samples near the surface
    surf = density > threshold
    weight = surf[..., None]
    wsum = surf.sum(axis=(1, 3, 5)).astype(np.float64)
    csum = (color * weight).sum(axis=(1, 3, 5))
    # a little blur along the surface, the model's colours are blotchy block to block
    if smooth:
        csum = np.stack([ndimage.gaussian_filter(csum[..., i], smooth) for i in range(3)], -1)
        wsum = ndimage.gaussian_filter(wsum, smooth)
    rgb = np.where(wsum[..., None] > 1e-6, csum / np.maximum(wsum, 1e-6)[..., None], color.mean(axis=(1, 3, 5)))

    lab = to_lab(np.clip(rgb, 0, 1) * 255)
    # the model's colours come out dull, pull them towards the photo's own range
    if photo is not None and len(photo):
        ref = to_lab(photo)
        seen = lab[shell]
        ratio = np.clip(ref.std(0) / np.maximum(seen.std(0), 1e-6), 0.5, 2)
        lab = (lab - seen.mean(0)) * ratio + ref.mean(0)

    grid = np.full(inside.shape, -1, dtype=np.int32)
    cells = tuple(np.argwhere(inside).T)
    grid[cells] = nearest_lab(lab[cells], names)
    return grid
