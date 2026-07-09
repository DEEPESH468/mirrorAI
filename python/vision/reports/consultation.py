from python.models.schemas import ConsultationReport, ExperienceMetadata, ExperienceResponse
from python.vision.beard.service import prepare_beard_overlay, render_beard
from python.vision.face.service import analyze_face, face_module_result
from python.vision.hair.hairstyle import prepare_hairstyle_overlay, render_hairstyle
from python.vision.hair.service import analyze_hair, hair_module_result, simulate_hair_color
from python.vision.makeup.service import makeup_module_result, render_makeup
from python.vision.reports.recommendation import build_recommendations, recommendation_module_result
from python.vision.skin.service import analyze_skin, skin_module_result
from python.vision.utils.image import DecodedImage


def prepare_consultation(metadata: ExperienceMetadata, image: DecodedImage) -> ExperienceResponse:
    face_analysis = analyze_face(image)
    modules = [face_module_result()]
    salon_render = None
    makeup_render = None
    hair_analysis = analyze_hair(image, face_analysis.mesh)
    skin_analysis = analyze_skin(image, face_analysis.mesh)

    if metadata.product in {"hair-analysis", "hair-color", "hairstyle"}:
        modules.append(hair_module_result())

    if metadata.product == "skin-analysis":
        modules.append(skin_module_result())

    if metadata.product == "makeup":
        modules.append(makeup_module_result())
        makeup_render = render_makeup(
            image=image,
            mesh=face_analysis.mesh,
            look_id=metadata.optionId or "soft-glam",
        )

    if metadata.product == "hairstyle":
        modules.append(prepare_hairstyle_overlay())
        salon_render = render_hairstyle(
            image=image,
            mesh=face_analysis.mesh,
            style_id=metadata.optionId or "crewcut",
            option_name=metadata.optionName,
        )

    if metadata.product == "beard":
        modules.append(prepare_beard_overlay())
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

    recommendations = build_recommendations(
        face_analysis.faceShape,
        hair_analysis,
        skin_analysis,
    )
    modules.append(recommendation_module_result())

    report = build_consultation_report(
        metadata=metadata,
        image=image,
        face_shape=face_analysis.faceShape,
        hair_analysis=hair_analysis,
        skin_analysis=skin_analysis,
        recommendations=recommendations,
        salon_render=salon_render or makeup_render,
        status="completed"
        if metadata.product
        in {"face-shape", "hairstyle", "beard", "hair-color", "hair-analysis", "skin-analysis", "makeup"}
        else "partial",
    )

    report_payload = report.model_dump()
    report_payload["modules"] = [module.model_dump() for module in modules]
    report_payload["optionId"] = metadata.optionId
    report_payload["optionName"] = metadata.optionName

    return ExperienceResponse(
        imageBase64=(salon_render.imageBase64 if salon_render else makeup_render.imageBase64 if makeup_render else None),
        aiResponse={
            "engine": face_analysis.engine,
            "status": report.status,
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
            "hair": hair_analysis.model_dump(),
            "skin": skin_analysis.model_dump(),
            "recommendations": recommendations.model_dump(),
            "salonRender": salon_render.model_dump() if salon_render else None,
            "makeupRender": makeup_render.model_dump() if makeup_render else None,
            "modules": [module.model_dump() for module in modules],
        },
        report=report_payload,
    )


def build_consultation_report(
    *,
    metadata: ExperienceMetadata,
    image: DecodedImage,
    face_shape,
    hair_analysis,
    skin_analysis,
    recommendations,
    salon_render,
    status: str,
) -> ConsultationReport:
    """Build the JSON report object; PDF export can later consume this schema."""

    return ConsultationReport(
        version="1.0",
        exportFormats=["json"],
        plannedExportFormats=["pdf"],
        product=metadata.product,
        productName=metadata.productName,
        status=status,  # type: ignore[arg-type]
        image={
            "width": image.width,
            "height": image.height,
            "contentType": image.content_type,
        },
        faceShape=face_shape,
        hair=hair_analysis,
        skin=skin_analysis,
        recommendations=recommendations,
        salonRender=salon_render,
        disclaimer=(
            "MirrorAI consultation reports are cosmetic best-effort estimates for salon planning. "
            "They are not medical, dermatological, or diagnostic advice."
        ),
    )
