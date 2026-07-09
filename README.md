# MirrorAI



The app is intentionally built for one classy salon brand. It is not a SaaS product and does not include authentication, payments, database storage, admin dashboards, booking, or multi-tenant accounts.

## Stack

- Next.js 15 App Router
- React 19
- TypeScript strict mode
- Tailwind CSS
- Framer Motion
- Lucide Icons

## Getting Started

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## YouCam Configuration

Set these environment variables in `.env.local` with the endpoint paths from the YouCam API console:

```bash
YOUCAM_API_KEY=...
YOUCAM_API_BASE_URL=...
YOUCAM_SKIN_ANALYSIS_ENDPOINT=...
YOUCAM_MAKEUP_ENDPOINT=...
YOUCAM_HAIR_COLOR_ENDPOINT=...
YOUCAM_HAIRSTYLE_ENDPOINT=...
YOUCAM_BEARD_ENDPOINT=...
YOUCAM_FACE_SHAPE_ENDPOINT=...
YOUCAM_HAIR_ANALYSIS_ENDPOINT=...
YOUCAM_API_TIMEOUT_MS=60000
```

The app posts multipart form data to `/api/youcam/[product]`, where `[product]` is one of:

- `skin-analysis`
- `makeup`
- `hair-color`
- `hairstyle`
- `beard`
- `face-shape`
- `hair-analysis`

Payloads always include `image`, `product`, and `productName`. Try-on modules also include option metadata and provider-style fields where applicable:

- Makeup: `look_id`, `optionId`, `optionName`
- Hair color: `color_id`, `optionId`, `optionName`
- Hairstyle: `style_id`, `optionId`, `optionName`
- Beard: `template_id`, `optionId`, `optionName`

If your API console shows different field names, update `src/lib/styles.ts` for option field mapping or `src/components/try-on/try-on-experience.tsx` for request assembly.

Proxy responses are normalized into:

```ts
{
  imageUrl?: string;
  imageBase64?: string;
  providerResponse: unknown;
}
```

Keep the API key server-only. Do not expose it with a `NEXT_PUBLIC_` prefix.

## Official YouCam Links

- Platform: https://yce.makeupar.com/ai-api
- API console: https://yce.makeupar.com/api-console/en/
- Pricing: https://yce.makeupar.com/ai-api/api-pricing
- Skin Analysis API: https://yce.makeupar.com/ai-api/products/skin-analysis-api
- Virtual Makeup Try-On API: https://yce.makeupar.com/ai-api/products/virtual-makeup-try-on-api
- Hair Color Changer API: https://yce.makeupar.com/ai-api/products/api-hair-color-changer
- Hairstyle API: https://yce.makeupar.com/ai-api/products/ai-hairstyle-api
- Beard API: https://yce.makeupar.com/ai-api/products/ai-beard-styles-api
- Face Shape Detector API: https://yce.makeupar.com/ai-api/products/face-shape-detector-api

## Project Structure

```text
src/
  app/
    api/youcam/[product]/route.ts
    try-on/page.tsx
    layout.tsx
    page.tsx
  components/
    site/
    try-on/
    ui/
  lib/
    styles.ts
    youcam.ts
  types/
    try-on.ts
```
