from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from python.models.schemas import ExperienceMetadata, ExperienceResponse, PRODUCT_IDS, is_product_id
from python.services.consultation import prepare_consultation
from python.utils.image import validate_image_upload


router = APIRouter(prefix="/api", tags=["experience"])


@router.post("/{product}", response_model=ExperienceResponse)
async def process_experience(
    product: str,
    image: UploadFile = File(...),
    product_name: str | None = Form(default=None, alias="productName"),
    option_id: str | None = Form(default=None, alias="optionId"),
    option_name: str | None = Form(default=None, alias="optionName"),
) -> ExperienceResponse:
    if not is_product_id(product):
        raise HTTPException(status_code=404, detail="Unsupported MirrorAI product.")

    try:
        image_bytes = await validate_image_upload(image)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    metadata = ExperienceMetadata(
        product=product,
        productName=product_name or product,
        optionId=option_id,
        optionName=option_name,
    )

    return prepare_consultation(metadata, len(image_bytes))


@router.get("/products", response_model=list[str])
def list_products() -> list[str]:
    return list(PRODUCT_IDS)
