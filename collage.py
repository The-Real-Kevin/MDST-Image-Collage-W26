from collections import defaultdict
import math

def euclidean_rgb(c1, c2):
    return math.sqrt(
        (c1[0] - c2[0]) ** 2 +
        (c1[1] - c2[1]) ** 2 +
        (c1[2] - c2[2]) ** 2
    )

def match_sections(sections, images, penalty=0.15):
    usage = defaultdict(int)
    matches = {}

    for sec_id, sec_color in sections.items():
        best_img = None
        best_score = float("inf")

        for img_id, img_color in images.items():
            d = euclidean_rgb(sec_color, img_color)
            d *= (1 + usage[img_id] * penalty)

            if d < best_score:
                best_score = d
                best_img = img_id

        matches[sec_id] = best_img
        usage[best_img] += 1

    return matches


import cv2
import numpy as np

def render_collage_cv(images, grid_w, grid_h, cell_size):
    canvas = np.zeros((grid_h * cell_size, grid_w * cell_size, 3), dtype=np.uint8)

    idx = 0
    for y in range(grid_h):
        for x in range(grid_w):
            if idx >= len(images):
                break

            img = cv2.resize(images[idx], (cell_size, cell_size))
            canvas[
                y*cell_size:(y+1)*cell_size,
                x*cell_size:(x+1)*cell_size
            ] = img

            idx += 1

    return canvas
