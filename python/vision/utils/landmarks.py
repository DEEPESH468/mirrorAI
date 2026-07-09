"""Shared MediaPipe landmark geometry helpers."""

import cv2
import numpy as np

from python.models.schemas import FaceMesh, Landmark


FACE_OVAL = (
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379,
    378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127,
    162, 21, 54, 103, 67, 109,
)
LIPS = (
    61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402,
    317, 14, 87, 178, 88, 95,
)
LEFT_EYE = (33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7)
RIGHT_EYE = (263, 466, 388, 387, 386, 385, 384, 398, 362, 382, 381, 380, 374, 373, 390, 249)


def landmark_map(mesh: FaceMesh) -> dict[int, Landmark]:
    return {landmark.index: landmark for landmark in mesh.landmarks}


def polygon_from_indices(mesh: FaceMesh, indices: tuple[int, ...] | list[int]) -> np.ndarray:
    points = []
    landmarks = landmark_map(mesh)
    for index in indices:
        if index in landmarks:
            point = landmarks[index]
            points.append([point.pixelX, point.pixelY])
    return np.array(points, dtype=np.int32)


def filled_mask(shape: tuple[int, int], points: np.ndarray) -> np.ndarray:
    mask = np.zeros(shape, dtype=np.uint8)
    if len(points) >= 3:
        cv2.fillPoly(mask, [points], 255)
    return mask


def face_mask(image_shape: tuple[int, int], mesh: FaceMesh) -> np.ndarray:
    return filled_mask(image_shape, polygon_from_indices(mesh, FACE_OVAL))


def softened(mask: np.ndarray, kernel_size: int = 21) -> np.ndarray:
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(mask, (kernel_size, kernel_size), 0)


def bbox(points: np.ndarray, padding: int, width: int, height: int) -> tuple[int, int, int, int]:
    x, y, w, h = cv2.boundingRect(points)
    x0 = max(x - padding, 0)
    y0 = max(y - padding, 0)
    x1 = min(x + w + padding, width)
    y1 = min(y + h + padding, height)
    return x0, y0, x1, y1


def level(score: float) -> str:
    if score >= 0.66:
        return "high"
    if score >= 0.34:
        return "moderate"
    return "low"
