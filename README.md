# MirrorAI

MirrorAI is a production-focused Next.js 15 website for a premium unisex salon. Guests can upload a portrait or use their camera through the existing frontend while the backend runs a local open-source face AI core.

The app is intentionally built for one classy salon brand. It is not a SaaS product and does not include authentication, payments, database storage, admin dashboards, booking, or multi-tenant accounts.

## Architecture

- Frontend: Next.js 15 App Router, React 19, TypeScript strict mode, Tailwind CSS, Framer Motion, Lucide Icons
- Local backend: Python FastAPI with OpenCV, MediaPipe, NumPy, Pillow, InsightFace, ONNX Runtime, and Segment Anything dependencies
- Integration boundary: reusable Next.js proxy route and TypeScript service wrappers

The browser posts images to the Next route `/api/ai/[product]`. Next forwards the multipart request to the local FastAPI backend at `MIRRORAI_AI_BACKEND_URL`.

The implemented AI core currently supports:

- Face detection with MediaPipe Face Detection
- Face mesh extraction with MediaPipe Face Mesh, returning 468 landmarks
- Face-shape detection for `oval`, `round`, `square`, `rectangle`, `diamond`, `heart`, and `triangle`
- Hairstyle try-on using transparent PNG assets aligned to Face Mesh landmarks
- Beard try-on using transparent PNG assets aligned to jaw and mouth landmarks
- Hair color simulation using OpenCV masking and local color blending

The browser camera flow, before/after comparison slider, and final image download are handled in the existing Next.js frontend.

## Getting Started

Install the web app:

```bash
npm install
cp .env.example .env.local
```

Install the local AI backend:

```bash
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r python/requirements.txt
```

Use Python 3.10, 3.11, or 3.12 for the AI backend. MediaPipe and related local
vision packages may not publish wheels for newer Python versions immediately.

Run the backend in one terminal:

```bash
npm run dev:ai
```

Run the web app in another terminal:

```bash
npm run dev:web
```

Open `http://localhost:3000`.

## Local Configuration

```bash
MIRRORAI_AI_BACKEND_URL=http://127.0.0.1:8000
MIRRORAI_AI_TIMEOUT_MS=120000
```

No remote service key is required. The backend uses only local open-source libraries.

## Supported Products

The app posts multipart form data to `/api/ai/[product]`, where `[product]` is one of:

- `skin-analysis`
- `makeup`
- `hair-color`
- `hairstyle`
- `beard`
- `face-shape`
- `hair-analysis`

Payloads always include `image`, `product`, and `productName`. Try-on modules also include option metadata and local style fields where applicable:

- Makeup: `look_id`, `optionId`, `optionName`
- Hair color: `color_id`, `optionId`, `optionName`
- Hairstyle: `style_id`, `optionId`, `optionName`
- Beard: `template_id`, `optionId`, `optionName`

Supported hair color ids:

- `black`
- `brown`
- `golden`
- `blonde`
- `silver`
- `red`
- `blue`

The `face-shape` product returns:

```ts
{
  imageBase64?: string;
  aiResponse: {
    engine: string;
    status: "completed";
    faceDetection: {
      confidence: number;
      boundingBox: Record<string, number>;
      keypoints: Record<string, { x: number; y: number }>;
    };
    faceMesh: {
      landmarkCount: 468;
      landmarks: Array<{
        index: number;
        x: number;
        y: number;
        z: number;
        pixelX: number;
        pixelY: number;
      }>;
    };
    faceShape: {
      shape: "oval" | "round" | "square" | "rectangle" | "diamond" | "heart" | "triangle";
      confidence: number;
      measurements: Record<string, number>;
      explanation: string;
    };
    modules: Array<unknown>;
  };
  report: Record<string, unknown>;
}
```

Product routes include face-core output, hair analysis, skin analysis, local
makeup rendering, recommendations, and a JSON consultation report payload.

## Face Core REST API

FastAPI also exposes dedicated face endpoints. All endpoints accept multipart
form data with an `image` file.

- `POST /api/face/detect`: returns primary face detection, confidence, keypoints, and bounding box
- `POST /api/face/mesh`: returns detection plus 468 Face Mesh landmarks
- `POST /api/face/shape`: returns detection, mesh, and face-shape classification
- `POST /api/face/analyze`: returns the complete face-core result

## Virtual Salon REST API

FastAPI exposes dedicated local rendering endpoints. All endpoints accept
multipart form data with an `image` file.

- `POST /api/salon/hairstyle`: accepts `style_id` and aligns a transparent PNG hairstyle asset
- `POST /api/salon/beard`: accepts `template_id` and aligns a transparent PNG beard asset
- `POST /api/salon/hair-color`: accepts `color_id` and applies an OpenCV hair-color mask
- `POST /api/salon/makeup`: accepts `look_id` and renders foundation, lipstick, blush, contour, eyeshadow, and eyeliner

Rendering responses include `imageBase64`, output dimensions, and the transform
metadata used by the module.

## Consultation Report API

- `POST /api/consultation/report`: returns a structured JSON consultation report

The report includes face shape, hair density, hair length, hair type, frizz,
cosmetic skin analysis, recommendations, confidence scores, and a disclaimer.
The schema includes `exportFormats: ["json"]` and `plannedExportFormats:
["pdf"]` so PDF export can be added later without reshaping the report
contract.

Validation and error behavior:

- `400`: missing file, non-image upload, decode failure, image too small, or file larger than 10 MB
- `422`: image is valid, but no face or no usable face mesh was found
- `404`: unsupported product id on `/api/[product]`

## AI Modules

`python/utils/image.py`: validates uploads with FastAPI, verifies image data with Pillow, decodes RGB arrays with OpenCV, and enforces minimum size and maximum payload rules.

`python/services/face_detection.py`: runs MediaPipe Face Detection locally and returns the highest-confidence face.

`python/services/face_mesh.py`: runs MediaPipe Face Mesh locally with iris refinement disabled so the response contains exactly 468 landmarks.

`python/services/face_shape.py`: classifies face shape from mesh geometry using cheekbone width, jaw width, forehead width, and face-height ratios.

`python/services/face.py`: orchestrates detection, mesh extraction, and face-shape classification for product and REST endpoints.

`python/services/assets.py`: loads transparent PNG hairstyle and beard assets from `public/assets/salon`, then scales, rotates, and composites them using face landmarks.

`python/services/hair.py`: runs OpenCV hair-region masking and blends supported hair colors while preserving image luminance.

`python/services/skin.py`: estimates acne-like visible spots, wrinkles, dark circles, redness, skin tone, and oiliness from local face-region image statistics. This is a cosmetic best-effort analysis, not a medical assessment.

`python/services/makeup.py`: renders local virtual makeup for lipstick, foundation, blush, contour, eyeshadow, and eyeliner.

`python/services/recommendation.py`: generates explainable hairstyle, beard, hair color, treatment, and product recommendations from face-shape, hair, and skin metrics.

`python/routers/face.py`: exposes dedicated REST endpoints for detection, mesh, shape, and full analysis.

`python/routers/salon.py`: exposes dedicated REST endpoints for hairstyle, beard, and hair-color rendering.

`python/routers/consultation.py`: exposes structured JSON consultation report export.

Transparent PNG assets live in:

```text
public/assets/salon/
  hairstyles/
    buzzcut.png
    crewcut.png
    curtain.png
    default.png
  beards/
    anchor.png
    bandholz.png
    goatee.png
    default.png
```

## Project Structure

```text
src/
  app/
    api/ai/[product]/route.ts
    try-on/page.tsx
    layout.tsx
    page.tsx
  components/
    site/
    try-on/
    ui/
  lib/
    ai/
      face.ts
      hairstyle.ts
      beard.ts
      hairColor.ts
      makeup.ts
      skin.ts
      recommendation.ts
      consultation.ts
    styles.ts
  types/
    try-on.ts

python/
  main.py
  routers/
    experience.py
    face.py
  models/
    schemas.py
  services/
    assets.py
    consultation.py
    face.py
    face_detection.py
    face_mesh.py
    face_shape.py
    hair.py
    makeup.py
    recommendation.py
    skin.py
  utils/
    image.py
  requirements.txt

public/
  assets/
    salon/
      hairstyles/
      beards/
```
