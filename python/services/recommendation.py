"""AI recommendation rules for salon consultations.

The recommendations are deterministic, local, and explainable. They consume the
computed face shape, hair analysis, and cosmetic skin analysis to produce ranked
salon suggestions with confidence scores.
"""

from python.models.schemas import (
    AiModuleResult,
    FaceShapeResult,
    HairAnalysisResult,
    RecommendationItem,
    RecommendationCategory,
    RecommendationSet,
    SkinAnalysisResult,
)


def recommendation_module_result() -> AiModuleResult:
    return AiModuleResult(
        module="recommendation",
        status="completed",
        message="Personalized salon recommendations generated from local analysis.",
    )


def build_recommendations(
    face_shape: FaceShapeResult | None,
    hair: HairAnalysisResult | None,
    skin: SkinAnalysisResult | None,
) -> RecommendationSet:
    shape = face_shape.shape if face_shape else "oval"

    return RecommendationSet(
        faceShape=face_shape,
        recommendedHairstyles=_hairstyles(shape, hair),
        recommendedBeardStyles=_beards(shape),
        recommendedHairColors=_hair_colors(shape, hair, skin),
        recommendedSalonTreatments=_treatments(hair, skin),
        recommendedProducts=_products(hair, skin),
    )


def _hairstyles(shape: str, hair: HairAnalysisResult | None) -> list[RecommendationItem]:
    mapping = {
        "round": [
            ("Curtain with height", "Adds vertical balance and soft face-framing movement.", 0.84),
            ("Textured crewcut", "Keeps sides cleaner while adding controlled top texture.", 0.78),
        ],
        "square": [
            ("Curtain layers", "Softens strong jaw lines with movement around the temples.", 0.82),
            ("Crewcut with texture", "Works with angular structure while keeping the profile polished.", 0.76),
        ],
        "rectangle": [
            ("Curtain volume", "Adds width around the sides to balance face length.", 0.83),
            ("Soft layered crop", "Avoids excessive height and keeps the look balanced.", 0.79),
        ],
        "diamond": [
            ("Curtain fringe", "Balances cheekbone width with softness at forehead and jaw.", 0.85),
            ("Textured crewcut", "Keeps proportions clean without widening cheekbones too much.", 0.75),
        ],
        "heart": [
            ("Curtain layers", "Softens forehead width and adds balance toward the lower face.", 0.84),
            ("Side-swept crop", "Creates diagonal movement and reduces top-heavy emphasis.", 0.77),
        ],
        "triangle": [
            ("Crewcut with volume", "Adds structure above the temples to balance a stronger jaw.", 0.82),
            ("Curtain with lift", "Adds upper-face width and a softer finish.", 0.78),
        ],
        "oval": [
            ("Crewcut", "Oval proportions support clean classic silhouettes.", 0.84),
            ("Curtain", "Adds salon movement while preserving balanced proportions.", 0.8),
        ],
    }
    items = mapping.get(shape, mapping["oval"])
    if hair and hair.frizz in {"moderate", "high"}:
        items.append(("Frizz-controlled textured cut", "Works with visible texture while keeping edges refined.", 0.76))
    return [_item("hairstyle", *item) for item in items[:3]]


def _beards(shape: str) -> list[RecommendationItem]:
    mapping = {
        "round": [("Anchor beard", "Adds definition under the chin and sharpens the lower face.", 0.82)],
        "square": [("Goatee", "Keeps grooming focused without over-widening the jaw.", 0.78)],
        "rectangle": [("Bandholz", "Adds side fullness to balance longer face proportions.", 0.8)],
        "diamond": [("Anchor beard", "Adds lower-face structure beneath prominent cheekbones.", 0.79)],
        "heart": [("Bandholz", "Adds fullness near the jaw to balance a broader forehead.", 0.8)],
        "triangle": [("Goatee", "Keeps the jaw cleaner while adding controlled central definition.", 0.77)],
        "oval": [("Anchor beard", "Maintains balanced proportions with a polished outline.", 0.81)],
    }
    return [_item("beard", *item) for item in mapping.get(shape, mapping["oval"])]


def _hair_colors(
    shape: str,
    hair: HairAnalysisResult | None,
    skin: SkinAnalysisResult | None,
) -> list[RecommendationItem]:
    tone = skin.skinTone if skin else "medium"
    base = [
        ("Brown gloss", "A dimensional brunette is versatile and salon-safe across most tones.", 0.8),
        ("Golden brunette", "Adds warmth and reflective shine without a drastic shift.", 0.74),
    ]
    if tone in {"fair", "light"}:
        base.insert(0, ("Blonde", "Brightens lighter skin tones with a soft salon finish.", 0.78))
    if tone in {"tan", "deep"}:
        base.insert(0, ("Black gloss", "Creates strong shine and contrast while keeping depth.", 0.79))
    if hair and hair.density == "low":
        base.append(("Soft brown dimension", "Lower-contrast color can make density look more natural.", 0.72))
    if shape in {"diamond", "heart"}:
        base.append(("Face-framing golden pieces", "Adds softness near forehead and cheekbone emphasis.", 0.73))
    return [_item("hair-color", *item) for item in base[:3]]


def _treatments(hair: HairAnalysisResult | None, skin: SkinAnalysisResult | None) -> list[RecommendationItem]:
    items: list[tuple[str, str, float]] = []
    if hair:
        if hair.frizz in {"moderate", "high"}:
            items.append(("Smoothing gloss treatment", "Visible texture suggests a shine and frizz-control service.", 0.82))
        if hair.density == "low":
            items.append(("Volume-building haircut consultation", "Lower visible density benefits from shape and lift planning.", 0.76))
        if hair.length in {"medium", "long"}:
            items.append(("Hydration mask", "Longer visible length benefits from moisture and end care.", 0.74))
    if skin:
        if skin.redness.level in {"moderate", "high"}:
            items.append(("Calming facial", "Visible redness suggests a gentle, soothing salon facial.", 0.76))
        if skin.oiliness.level in {"moderate", "high"}:
            items.append(("Balancing cleanse treatment", "T-zone shine suggests a balancing, non-stripping service.", 0.74))
        if skin.darkCircles.level in {"moderate", "high"}:
            items.append(("Brightening eye add-on", "Under-eye shadowing appears more visible in the portrait.", 0.7))
    if not items:
        items.append(("Signature consultation", "Overall visual balance supports a standard stylist-led consultation.", 0.68))
    return [_item("salon-treatment", *item) for item in items[:4]]


def _products(hair: HairAnalysisResult | None, skin: SkinAnalysisResult | None) -> list[RecommendationItem]:
    items: list[tuple[str, str, float]] = []
    if hair and hair.frizz in {"moderate", "high"}:
        items.append(("Anti-frizz serum", "Helps polish visible flyaway texture.", 0.8))
    if hair and hair.density == "low":
        items.append(("Lightweight volumizing spray", "Adds lift without weighing down lower visible density.", 0.76))
    if skin and skin.oiliness.level in {"moderate", "high"}:
        items.append(("Oil-control primer", "Helps reduce visible T-zone shine before makeup.", 0.78))
    if skin and skin.redness.level in {"moderate", "high"}:
        items.append(("Green-neutralizing base", "Can visually soften red areas before foundation.", 0.74))
    if skin and skin.darkCircles.level in {"moderate", "high"}:
        items.append(("Peach corrector", "Helps balance visible under-eye darkness.", 0.72))
    if not items:
        items.append(("Heat protectant spray", "A reliable baseline product for salon styling prep.", 0.68))
    return [_item("product", *item) for item in items[:4]]


def _item(
    category: RecommendationCategory,
    title: str,
    reason: str,
    confidence: float,
) -> RecommendationItem:
    return RecommendationItem(
        category=category,
        title=title,
        reason=reason,
        confidence=round(confidence, 4),
    )
