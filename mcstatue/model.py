import numpy as np
import rembg
import torch
from PIL import Image

from tsr.system import TSR

THRESHOLD = 25.0


def load(threads=None):
    if threads:
        torch.set_num_threads(threads)
    model = TSR.from_pretrained("stabilityai/TripoSR", config_name="config.yaml", weight_name="model.ckpt")
    model.renderer.set_chunk_size(8192)
    return model


def cutout(path):
    """object on a grey square, the way TripoSR was trained"""
    img = Image.open(path).convert("RGBA")
    if img.getextrema()[3][0] == 255:
        img = rembg.remove(img, session=rembg.new_session("isnet-general-use"))
    a = np.array(img)
    ys, xs = np.nonzero(a[..., 3] > 0)
    fg = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    side = int(max(fg.shape[:2]) / 0.85)
    canvas = np.zeros((side, side, 4), np.uint8)
    y, x = (side - fg.shape[0]) // 2, (side - fg.shape[1]) // 2
    canvas[y:y + fg.shape[0], x:x + fg.shape[1]] = fg
    c = canvas.astype(np.float32) / 255
    rgb = c[..., :3] * c[..., 3:] + (1 - c[..., 3:]) * 0.5
    return Image.fromarray((rgb * 255).astype(np.uint8))


def sample(model, image, height, s=2):
    """density and colour, s samples per block edge, in Minecraft axes (x, y up, z facing the camera)"""
    with torch.no_grad():
        code = model([image], "cpu")[0]

    def query(axes):
        pts = np.stack(np.meshgrid(*axes, indexing="ij"), -1)
        with torch.no_grad():
            out = model.renderer.query_triplane(model.decoder, torch.tensor(pts.reshape(-1, 3), dtype=torch.float32), code)
        shape = pts.shape[:3]
        return out["density_act"].numpy().reshape(shape), out["color"].numpy().reshape(shape + (3,))

    # rough pass to find where the object is, then sample just that box at block size
    r = model.renderer.cfg.radius
    g = np.linspace(-r, r, 96)
    density, _ = query([g, g, g])
    cells = np.argwhere(density > THRESHOLD)
    if len(cells) == 0:
        raise ValueError("the model didn't find an object in the photo")
    step = g[1] - g[0]
    lo, hi = g[cells.min(0)] - step, g[cells.max(0)] + step
    block = (hi[2] - lo[2]) / height  # TripoSR is z up
    n = np.ceil((hi - lo) / block).astype(int)
    density, color = query([lo[i] + (np.arange(n[i] * s) + 0.5) * block / s for i in range(3)])

    # TripoSR (x, y, z up) to Minecraft (x, y up, z)
    flip = lambda a: a[::-1, ::-1].transpose((1, 2, 0) + tuple(range(3, a.ndim)))
    return flip(density), flip(color)
