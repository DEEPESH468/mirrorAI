from python.models.schemas import ExperienceMetadata, ExperienceResponse
from python.services.assets import prepare_asset_overlay, render_beard, render_hairstyle
from python.services.face import analyze_face, face_module_result
from python.services.hair import analyze_hair, simulate_hair_color
from python.services.makeup import apply_makeup
from python.services.recommendation import build_recommendations
from python.services.skin import analyze_skin
from python.utils.image import DecodedImage


def prepare_consultation(metadata: ExperienceMetadata, image: DecodedImage) -> ExperienceResponse:
    face_analysis = analyze_face(image)
    modules = [face_module_result()]
    salon_render = None

    if metadata.product in {"hair-analysis", "hair-color", "hairstyle"}:
        modules.append(analyze_hair())

    if metadata.product == "skin-analysis":
        modules.append(analyze_skin())

    if metadata.product == "makeup":
        modules.append(apply_makeup())

    if metadata.product == "hairstyle":
        modules.append(prepare_asset_overlay("hairstyle"))
        salon_render = render_hairstyle(
            image=image,
            mesh=face_analysis.mesh,
            style_id=metadata.optionId or "crewcut",
            option_name=metadata.optionName,
        )

    if metadata.product == "beard":
        modules.append(prepare_asset_overlay("beard"))
        salon_render = render_beard(
            image=image,
            mesh=face_analysis.mesh,
            template_id=metadata.optionId or "anchor",
            option_name=metadata.optionName,
        )

    if metadata.product == "hair-color":
        salon_render = simulate_hair_color(
            image=image,
            mesh=face_analysis.mesh,
            color_id=metadata.optionId or "brown",
            option_name=metadata.optionName,
        )

    modules.append(build_recommendations())

    report = {
        "product": metadata.product,
        "productName": metadata.productName,
        "optionId": metadata.optionId,
        "optionName": metadata.optionName,
        "status": "completed" if metadata.product in {"face-shape", "hairstyle", "beard", "hair-color"} else "partial",
        "modules": [module.model_dump() for module in modules],
        "faceShape": face_analysis.faceShape.model_dump() if face_analysis.faceShape else None,
        "salonRender": salon_render.model_dump() if salon_render else None,
    }

    return ExperienceResponse(
        imageBase64=salon_render.imageBase64 if salon_render else None,
        aiResponse={
            "engine": face_analysis.engine,
            "status": "completed" if metadata.product in {"face-shape", "hairstyle", "beard", "hair-color"} else "partial",
            "imageSizeBytes": len(image.data),
            "faceDetection": face_analysis.detection.model_dump(),
            "faceMesh": {
                "landmarkCount": face_analysis.mesh.landmarkCount,
                "landmarks": [
                    landmark.model_dump() for landmark in face_analysis.mesh.landmarks
                ],
            }
            if face_analysis.mesh
            else None,
            "faceShape": face_analysis.faceShape.model_dump() if face_analysis.faceShape else None,
            "salonRender": salon_render.model_dump() if salon_render else None,
            "modules": [module.model_dump() for module in modules],
        },
        report=report,
    )
