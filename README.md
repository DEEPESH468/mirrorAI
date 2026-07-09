# MirrorAI

MirrorAI is a production-focused Next.js 15 website for a premium unisex salon. Guests can upload a portrait or use their camera through the existing frontend while the backend is prepared for future self-hosted salon AI modules.

The app is intentionally built for one classy salon brand. It is not a SaaS product and does not include authentication, payments, database storage, admin dashboards, booking, or multi-tenant accounts.

## Architecture

- Frontend: Next.js 15 App Router, React 19, TypeScript strict mode, Tailwind CSS, Framer Motion, Lucide Icons
- Local backend: Python FastAPI
- Integration boundary: reusable Next.js proxy route and TypeScript service wrappers

The browser posts images to the Next route `/api/ai/[product]`. Next forwards the multipart request to the local FastAPI backend at `MIRRORAI_AI_BACKEND_URL`. AI modules are intentionally scaffolded only and return structured `not_implemented` module statuses.

## Getting Started

Install the web app:

```bash
npm install
cp .env.example .env.local
```

Install the local AI backend:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r python/requirements.txt
```

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

No remote service key is required.

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

The scaffold backend returns:

```ts
{
  imageBase64?: string;
  aiResponse: {
    engine: string;
    status: "not_implemented";
    modules: Array<unknown>;
  };
  report: Record<string, unknown>;
}
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
  models/
    schemas.py
  services/
    assets.py
    consultation.py
    face.py
    hair.py
    makeup.py
    recommendation.py
    skin.py
  utils/
    image.py
  requirements.txt
```
