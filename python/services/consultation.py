from python.models.schemas import ExperienceMetadata, ExperienceResponse
from python.services.assets import prepare_asset_overlay
from python.services.face import analyze_face
from python.services.hair import analyze_hair
from python.services.makeup import apply_makeup
from python.services.recommendation import build_recommendations
from python.services.skin import analyze_skin


def prepare_consultation(metadata: ExperienceMetadata, image_size_bytes: int) -> ExperienceResponse:
    modules = [analyze_face()]

    if metadata.product in {"hair-analysis", "hair-color", "hairstyle"}:
        modules.append(analyze_hair())

    if metadata.product == "skin-analysis":
        modules.append(analyze_skin())

    if metadata.product == "makeup":
        modules.append(apply_makeup())

    if metadata.product == "hairstyle":
        modules.append(prepare_asset_overlay("hairstyle"))

    if metadata.product == "beard":
        modules.append(prepare_asset_overlay("beard"))

    modules.append(build_recommendations())

    report = {
        "product": metadata.product,
        "productName": metadata.productName,
        "optionId": metadata.optionId,
        "optionName": metadata.optionName,
        "status": "not_implemented",
        "modules": [module.model_dump() for module in modules],
    }

    return ExperienceResponse(
        imageBase64=None,
        aiResponse={
            "engine": "MirrorAI local FastAPI backend",
            "status": "not_implemented",
            "imageSizeBytes": image_size_bytes,
            "modules": [module.model_dump() for module in modules],
        },
        report=report,
    )
