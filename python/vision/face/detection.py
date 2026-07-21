"""MediaPipe face detection service.

This module runs the free MediaPipe Face Detection model locally. It returns a
single highest-confidence face with normalized and pixel-space bounding boxes.
No external API call is made.
"""

from collections.abc import Mapping
import os

import cv2
import mediapipe as mp
import numpy as np

from python.models.schemas import BoundingBox, FaceDetection


KEYPOINT_NAMES = (
    "rightEye",
    "leftEye",
    "noseTip",
    "mouthCenter",
    "rightEarTragion",
    "leftEarTragion",
)


class FaceDetectionError(ValueError):
    """Raised when a portrait image does not contain a detectable face."""


def detect_primary_face(
    rgb_image: np.ndarray,
    min_confidence: float = 0.5,
) -> FaceDetection:
    """Detect the primary face in an RGB image using MediaPipe."""

    height, width = rgb_image.shape[:2]

    # ---------------- DEBUG ----------------
    os.makedirs("python/debug", exist_ok=True)

    print("\n========== FACE DETECTION DEBUG ==========")
    print("Shape :", rgb_image.shape)
    print("Dtype :", rgb_image.dtype)
    print("Min   :", rgb_image.min())
    print("Max   :", rgb_image.max())

    debug_path = "python/debug/input.jpg"

    try:
        cv2.imwrite(
            debug_path,
            cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR),
        )
        print(f"Saved debug image -> {debug_path}")
    except Exception as e:
        print("Failed to save debug image:", e)

    print("=========================================\n")

    # ---------------- MediaPipe ----------------

    face_detection = mp.solutions.face_detection

    with face_detection.FaceDetection(
        model_selection=0,
        min_detection_confidence=0.3,
    ) as detector:

        result = detector.process(rgb_image)

        print("MediaPipe detections:", result.detections)

        if result.detections:
            print("Number of detections:", len(result.detections))
            print("Confidence:", result.detections[0].score)

    if not result.detections:
        raise FaceDetectionError(
            "No face was detected. Upload a clear front-facing portrait."
        )

    detection = max(
        result.detections,
        key=lambda item: item.score[0] if item.score else 0.0,
    )

    location = detection.location_data
    relative_box = location.relative_bounding_box

    x_min = max(relative_box.xmin, 0.0)
    y_min = max(relative_box.ymin, 0.0)
    box_width = min(relative_box.width, 1.0 - x_min)
    box_height = min(relative_box.height, 1.0 - y_min)

    keypoints = {}

    for index, keypoint in enumerate(location.relative_keypoints):
        name = (
            KEYPOINT_NAMES[index]
            if index < len(KEYPOINT_NAMES)
            else f"keypoint{index}"
        )

        keypoints[name] = {
            "x": round(float(keypoint.x), 6),
            "y": round(float(keypoint.y), 6),
        }

    return FaceDetection(
        confidence=round(float(detection.score[0]), 6),
        boundingBox=BoundingBox(
            x=round(x_min * width),
            y=round(y_min * height),
            width=round(box_width * width),
            height=round(box_height * height),
            xMin=round(float(x_min), 6),
            yMin=round(float(y_min), 6),
            widthRatio=round(float(box_width), 6),
            heightRatio=round(float(box_height), 6),
        ),
        keypoints=_round_keypoints(keypoints),
    )


def _round_keypoints(
    keypoints: Mapping[str, Mapping[str, float]],
) -> dict[str, dict[str, float]]:
    return {
        name: {
            "x": round(float(point["x"]), 6),
            "y": round(float(point["y"]), 6),
        }
        for name, point in keypoints.items()
    }