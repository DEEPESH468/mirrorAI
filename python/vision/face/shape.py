"""Face-shape classification from MediaPipe landmarks.

The classifier is a deterministic geometric heuristic, not a learned identity
model. It compares face height, cheekbone width, jaw width, and forehead width
from stable Face Mesh landmark regions to classify oval, round, square,
rectangle, diamond, heart, or triangle face shapes.
"""

from math import hypot

from python.models.schemas import FaceMesh, FaceShapeMeasurements, FaceShapeResult, Landmark


class FaceShapeError(ValueError):
    """Raised when landmarks are insufficient for face-shape classification."""


def classify_face_shape(mesh: FaceMesh) -> FaceShapeResult:
    """Classify face shape using 468 MediaPipe landmarks.

    Args:
        mesh: FaceMesh containing MediaPipe's 468 landmark output.

    Returns:
        A structured face-shape result with measurements and explanation.

    Raises:
        FaceShapeError: If the mesh does not contain all required landmarks.
    """

    landmarks = {landmark.index: landmark for landmark in mesh.landmarks}
    required = (10, 152, 127, 356, 234, 454, 172, 397, 58, 288)

    if any(index not in landmarks for index in required):
        raise FaceShapeError("Face mesh does not include enough landmarks for shape analysis.")

    forehead_width = _distance(landmarks[127], landmarks[356])
    cheekbone_width = _distance(landmarks[234], landmarks[454])
    jaw_width = max(
        _distance(landmarks[172], landmarks[397]),
        _distance(landmarks[58], landmarks[288]),
    )
    face_height = _distance(landmarks[10], landmarks[152])

    if cheekbone_width <= 0 or face_height <= 0:
        raise FaceShapeError("Face landmarks were too compressed for reliable shape analysis.")

    height_to_width = face_height / cheekbone_width
    jaw_to_cheek = jaw_width / cheekbone_width
    forehead_to_cheek = forehead_width / cheekbone_width

    shape, confidence, explanation = _choose_shape(
        height_to_width=height_to_width,
        jaw_to_cheek=jaw_to_cheek,
        forehead_to_cheek=forehead_to_cheek,
    )

    return FaceShapeResult(
        shape=shape,
        confidence=confidence,
        measurements=FaceShapeMeasurements(
            faceHeight=round(face_height, 3),
            cheekboneWidth=round(cheekbone_width, 3),
            jawWidth=round(jaw_width, 3),
            foreheadWidth=round(forehead_width, 3),
            heightToWidthRatio=round(height_to_width, 4),
            jawToCheekRatio=round(jaw_to_cheek, 4),
            foreheadToCheekRatio=round(forehead_to_cheek, 4),
        ),
        explanation=explanation,
    )


def _distance(first: Landmark, second: Landmark) -> float:
    return hypot(first.pixelX - second.pixelX, first.pixelY - second.pixelY)


def _choose_shape(
    *,
    height_to_width: float,
    jaw_to_cheek: float,
    forehead_to_cheek: float,
) -> tuple[str, float, str]:
    if jaw_to_cheek >= 0.9 and forehead_to_cheek <= 0.82:
        return (
            "triangle",
            _confidence(jaw_to_cheek - forehead_to_cheek, 0.08),
            "Jaw width is noticeably stronger than the forehead.",
        )

    if forehead_to_cheek >= 0.92 and jaw_to_cheek <= 0.72:
        return (
            "heart",
            _confidence(forehead_to_cheek - jaw_to_cheek, 0.16),
            "Forehead width is broad while the jaw tapers toward the chin.",
        )

    if forehead_to_cheek <= 0.82 and jaw_to_cheek <= 0.76:
        return (
            "diamond",
            _confidence(1.0 - max(forehead_to_cheek, jaw_to_cheek), 0.18),
            "Cheekbones are the widest region with narrower forehead and jaw.",
        )

    if height_to_width <= 1.24 and jaw_to_cheek >= 0.78:
        return (
            "round",
            _confidence(1.28 - height_to_width, 0.08),
            "Face height and width are close, with soft width through the jaw.",
        )

    if height_to_width >= 1.46 and jaw_to_cheek >= 0.78:
        return (
            "rectangle",
            _confidence(height_to_width - 1.36, 0.12),
            "Face length is dominant while forehead, cheek, and jaw widths stay aligned.",
        )

    if jaw_to_cheek >= 0.82 and forehead_to_cheek >= 0.84:
        return (
            "square",
            _confidence(jaw_to_cheek, 0.78),
            "Forehead, cheekbones, and jaw read as similarly broad.",
        )

    return (
        "oval",
        _confidence(height_to_width, 1.28),
        "Face length is greater than width with a softly tapered jaw.",
    )


def _confidence(value: float, baseline: float) -> float:
    score = 0.62 + min(abs(value - baseline), 0.28)
    return round(min(score, 0.92), 4)
