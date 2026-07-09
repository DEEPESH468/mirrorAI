"""MediaPipe Face Mesh service.

The local model extracts the canonical 468 facial landmarks. Iris refinement is
disabled intentionally so the output stays at exactly 468 landmarks.
"""

import mediapipe as mp
import numpy as np

from python.models.schemas import FaceMesh, Landmark


class FaceMeshError(ValueError):
    """Raised when MediaPipe cannot produce a face mesh."""


def extract_face_mesh(rgb_image: np.ndarray) -> FaceMesh:
    """Extract 468 face landmarks from an RGB image.

    Args:
        rgb_image: RGB image array with shape ``height x width x 3``.

    Returns:
        A structured FaceMesh object containing 468 landmarks.

    Raises:
        FaceMeshError: If no mesh can be extracted.
    """

    height, width = rgb_image.shape[:2]
    face_mesh = mp.solutions.face_mesh

    with face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.5,
    ) as mesh:
        result = mesh.process(rgb_image)

    if not result.multi_face_landmarks:
        raise FaceMeshError("A face was detected, but facial landmarks could not be extracted.")

    landmarks = result.multi_face_landmarks[0].landmark[:468]

    return FaceMesh(
        landmarkCount=len(landmarks),
        landmarks=[
            Landmark(
                index=index,
                x=round(float(point.x), 6),
                y=round(float(point.y), 6),
                z=round(float(point.z), 6),
                pixelX=round(float(point.x) * width),
                pixelY=round(float(point.y) * height),
            )
            for index, point in enumerate(landmarks)
        ],
    )
