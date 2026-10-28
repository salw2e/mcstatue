import numpy as np

# average texture colour of each full block
COLORS = {
    "white_wool": (234, 236, 237),
    "white_concrete": (207, 213, 214),
    "white_terracotta": (210, 178, 161),
    "orange_wool": (241, 118, 20),
    "orange_concrete": (224, 97, 1),
    "orange_terracotta": (162, 84, 38),
    "magenta_wool": (190, 69, 180),
    "magenta_concrete": (169, 48, 159),
    "magenta_terracotta": (150, 88, 109),
    "light_blue_wool": (58, 175, 217),
    "light_blue_concrete": (36, 137, 199),
    "light_blue_terracotta": (113, 109, 138),
    "yellow_wool": (249, 198, 40),
    "yellow_concrete": (241, 175, 21),
    "yellow_terracotta": (186, 133, 35),
    "lime_wool": (112, 185, 26),
    "lime_concrete": (94, 169, 24),
    "lime_terracotta": (104, 118, 53),
    "pink_wool": (238, 141, 172),
    "pink_concrete": (214, 101, 143),
    "pink_terracotta": (162, 78, 79),
    "gray_wool": (63, 68, 72),
    "gray_concrete": (55, 58, 62),
    "gray_terracotta": (58, 42, 36),
    "light_gray_wool": (142, 142, 135),
    "light_gray_concrete": (125, 125, 115),
    "light_gray_terracotta": (135, 107, 98),
    "cyan_wool": (21, 138, 145),
    "cyan_concrete": (21, 119, 136),
    "cyan_terracotta": (87, 91, 91),
    "purple_wool": (122, 42, 173),
    "purple_concrete": (100, 32, 156),
    "purple_terracotta": (118, 70, 86),
    "blue_wool": (53, 57, 157),
    "blue_concrete": (45, 47, 143),
    "blue_terracotta": (74, 60, 91),
    "brown_wool": (114, 72, 41),
    "brown_concrete": (96, 60, 32),
    "brown_terracotta": (77, 51, 36),
    "green_wool": (85, 110, 28),
    "green_concrete": (73, 91, 36),
    "green_terracotta": (76, 83, 42),
    "red_wool": (161, 39, 35),
    "red_concrete": (142, 33, 33),
    "red_terracotta": (143, 61, 47),
    "black_wool": (21, 21, 26),
    "black_concrete": (8, 10, 15),
    "black_terracotta": (37, 23, 16),
    "terracotta": (152, 94, 68),
    "oak_planks": (162, 131, 79),
    "spruce_planks": (115, 85, 49),
    "birch_planks": (192, 175, 121),
    "jungle_planks": (160, 115, 81),
    "acacia_planks": (168, 90, 50),
    "dark_oak_planks": (67, 43, 20),
    "mangrove_planks": (118, 54, 49),
    "cherry_planks": (227, 179, 173),
    "bamboo_planks": (193, 173, 80),
    "crimson_planks": (101, 49, 71),
    "warped_planks": (43, 105, 99),
    "stone": (126, 126, 126),
    "cobblestone": (128, 127, 128),
    "stone_bricks": (122, 122, 122),
    "mossy_stone_bricks": (115, 121, 105),
    "mossy_cobblestone": (110, 118, 95),
    "smooth_stone": (159, 159, 159),
    "andesite": (136, 136, 137),
    "polished_andesite": (132, 135, 134),
    "diorite": (189, 188, 189),
    "polished_diorite": (193, 193, 195),
    "granite": (149, 103, 86),
    "polished_granite": (154, 107, 89),
    "cobbled_deepslate": (77, 77, 81),
    "deepslate_bricks": (71, 71, 71),
    "deepslate_tiles": (55, 55, 55),
    "polished_deepslate": (72, 73, 73),
    "tuff": (108, 109, 103),
    "calcite": (223, 224, 221),
    "dripstone_block": (134, 108, 93),
    "polished_blackstone": (53, 49, 57),
    "polished_blackstone_bricks": (48, 43, 50),
    "bricks": (151, 98, 83),
    "mud_bricks": (137, 104, 79),
    "packed_mud": (142, 107, 80),
    "prismarine": (98, 162, 146),
    "prismarine_bricks": (99, 172, 158),
    "dark_prismarine": (52, 92, 76),
    "end_stone": (220, 223, 158),
    "end_stone_bricks": (218, 224, 162),
    "purpur_block": (170, 126, 170),
    "nether_bricks": (44, 22, 26),
    "red_nether_bricks": (70, 7, 9),
    "netherrack": (98, 38, 38),
    "nether_wart_block": (115, 3, 2),
    "warped_wart_block": (23, 120, 121),
    "obsidian": (15, 11, 25),
    "clay": (161, 166, 179),
    "packed_ice": (142, 180, 250),
    "blue_ice": (116, 168, 253),
    "moss_block": (89, 110, 45),
    "gold_block": (246, 208, 62),
    "iron_block": (220, 220, 220),
    "diamond_block": (98, 237, 228),
    "emerald_block": (42, 203, 88),
    "lapis_block": (31, 67, 140),
    "redstone_block": (176, 25, 5),
    "coal_block": (16, 16, 16),
    "amethyst_block": (134, 98, 191),
    "honeycomb_block": (229, 148, 30),
    "raw_iron_block": (166, 136, 107),
    "raw_gold_block": (222, 169, 47),
    "raw_copper_block": (154, 106, 79),
    "snow_block": (249, 254, 254),
    "quartz_block": (236, 230, 223),
    "smooth_quartz": (237, 230, 224),
    "smooth_sandstone": (224, 214, 170),
    "smooth_red_sandstone": (181, 98, 31),
    "hay_block": (166, 137, 38),
    "bone_block": (229, 226, 208),
    "waxed_copper_block": (192, 108, 80),
    "waxed_exposed_copper": (161, 126, 104),
    "waxed_weathered_copper": (108, 153, 110),
    "waxed_oxidized_copper": (82, 163, 133),
    "deepslate": (80, 80, 83),
    "blackstone": (42, 36, 41),
    "sandstone": (216, 203, 156),
    "red_sandstone": (187, 99, 29),
    "melon": (114, 146, 30),
    "pumpkin": (196, 115, 24),
    "dried_kelp_block": (38, 49, 30),
}

GROUPS = {
    "wool": [b for b in COLORS if b.endswith("_wool")],
    "concrete": [b for b in COLORS if b.endswith("_concrete")],
    "terracotta": [b for b in COLORS if b.endswith("terracotta")],
}


def palette(spec="all"):
    if spec == "all":
        return list(COLORS)
    names = []
    for part in spec.split(","):
        part = part.strip().removeprefix("minecraft:")
        if part in GROUPS:
            names += GROUPS[part]
        elif part in COLORS:
            names.append(part)
        else:
            raise ValueError(f"unknown block or group: {part}")
    return list(dict.fromkeys(names))


def to_lab(rgb):
    c = np.asarray(rgb, dtype=np.float64) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.4124, 0.2126, 0.0193], [0.3576, 0.7152, 0.1192], [0.1805, 0.0722, 0.9505]])
    xyz /= [0.95047, 1.0, 1.08883]
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def nearest(rgb, names):
    return nearest_lab(to_lab(rgb), names)


def nearest_lab(lab, names):
    pal = to_lab([COLORS[n] for n in names])
    d = ((lab[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    return d.argmin(1)
