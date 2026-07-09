"""MediaPipe face detection service.

This module runs the free MediaPipe Face Detection model locally. It returns a
single highest-confidence face with normalized and pixel-space bounding boxes.
No external API call is made.
"""

from collections.abc import Mapping

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


def detect_primary_face(rgb_image: np.ndarray, min_confidence: float = 0.5) -> FaceDetection:
    """Detect the primary face in an RGB image using MediaPipe.

    Args:
        rgb_image: RGB image array with shape ``height x width x 3``.
        min_confidence: Minimum MediaPipe detection confidence.

    Returns:
        A structured face detection result for the highest-confidence face.

    Raises:
        FaceDetectionError: If no face can be detected.
    """

    height, width = rgb_image.shape[:2]
    face_detection = mp.solutions.face_detection

    with face_detection.FaceDetection(
        model_selection=1,
        min_detection_confidence=min_confidence,
    ) as detector:
        result = detector.process(rgb_image)

    if not result.detections:
        raise FaceDetectionError("No face was detected. Upload a clear front-facing portrait.")

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

    keypoints: dict[str, dict[str, float]] = {}
    for index, keypoint in enumerate(location.relative_keypoints):
        name = KEYPOINT_NAMES[index] if index < len(KEYPOINT_NAMES) else f"keypoint{index}"
        keypoints[name] = {
            "x": round(float(keypoint.x), 6),
            "y": round(float(keypoint.y), 6),
        }

    return FaceDetection(
        confidence=round(float(detection.score[0]), 6) if detection.score else 0.0,
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


def _round_keypoints(keypoints: Mapping[str, Mapping[str, float]]) -> dict[str, dict[str, float]]:
    return {
        name: {
            "x": round(float(point["x"]), 6),
            "y": round(float(point["y"]), 6),
        }
        for name, point in keypoints.items()
    }
