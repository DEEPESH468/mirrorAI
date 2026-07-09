"use client";

import { motion } from "framer-motion";
import {
  Activity,
  AlertCircle,
  BadgeCheck,
  Brush,
  Camera,
  Check,
  Download,
  Droplets,
  FileText,
  ImageUp,
  Palette,
  RefreshCcw,
  ScanFace,
  Scissors,
  Sparkles,
  Upload,
  WandSparkles
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  experienceProducts,
  getOptionsByCategory,
  getProductByCategory
} from "@/lib/styles";
import type {
  ExperienceCategory,
  ExperienceOption,
  ExperienceResult
} from "@/types/try-on";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";

type SourceMode = "upload" | "camera";

const productIcons: Record<ExperienceCategory, React.ElementType> = {
  "skin-analysis": Droplets,
  makeup: Brush,
  "hair-color": Palette,
  hairstyle: Scissors,
  beard: WandSparkles,
  "face-shape": ScanFace,
  "hair-analysis": Activity
};

export function TryOnExperience() {
  const [category, setCategory] = useState<ExperienceCategory>("skin-analysis");
  const product = getProductByCategory(category) ?? experienceProducts[0];
  const options = useMemo(() => getOptionsByCategory(category), [category]);
  const [selectedOption, setSelectedOption] = useState<ExperienceOption | null>(
    options[0] ?? null
  );
  const [sourceMode, setSourceMode] = useState<SourceMode>("upload");
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<ExperienceResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [comparison, setComparison] = useState(50);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    setSelectedOption(options[0] ?? null);
  }, [options]);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      stopCamera();
    };
  }, [previewUrl]);

  const resultSource =
    result?.imageUrl ??
    (result?.imageBase64
      ? result.imageBase64.startsWith("data:")
        ? result.imageBase64
        : `data:image/jpeg;base64,${result.imageBase64}`
      : undefined);
  const reportItems = useMemo(
    () => buildReportItems(result?.aiResponse),
    [result?.aiResponse]
  );

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setIsCameraActive(false);
  }

  function updatePhoto(file: File) {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPhotoFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setComparison(50);
  }

  async function startCamera() {
    setError(null);
    setSourceMode("camera");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 1280 } },
        audio: false
      });

      streamRef.current = stream;
      setIsCameraActive(true);

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
    } catch {
      setError("Camera access was blocked. Upload a portrait instead or allow camera access.");
    }
  }

  async function capturePhoto() {
    const video = videoRef.current;

    if (!video) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");

    if (!context) {
      setError("Unable to capture from the camera on this device.");
      return;
    }

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (!blob) {
        setError("Unable to save the captured image.");
        return;
      }

      updatePhoto(new File([blob], "mirrorai-camera-capture.jpg", { type: "image/jpeg" }));
      stopCamera();
    }, "image/jpeg", 0.92);
  }

  async function runExperience() {
    if (!photoFile) {
      setError("Upload or capture a clear portrait first.");
      return;
    }

    if (product.mode === "try-on" && !selectedOption) {
      setError("Select a look before generating your preview.");
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("image", photoFile);
    formData.append("product", product.id);
    formData.append("productName", product.name);

    if (selectedOption) {
      if (selectedOption.localField) {
        formData.append(selectedOption.localField, selectedOption.id);
      }

      formData.append("optionId", selectedOption.id);
      formData.append("optionName", selectedOption.name);
    }

    try {
      const response = await fetch(`/api/ai/${category}`, {
        method: "POST",
        body: formData
      });
      const payload = (await response.json()) as ExperienceResult | { message?: string };

      if (!response.ok) {
        throw new Error(
          "message" in payload && payload.message
            ? payload.message
            : "The AI salon request failed."
        );
      }

      setResult(payload as ExperienceResult);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Something went wrong while preparing your salon experience."
      );
    } finally {
      setIsProcessing(false);
    }
  }

  return (
    <section className="px-5 pb-16 pt-28 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--copper-dark)]">
            AI Salon Suite
          </p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight text-[var(--ink)] sm:text-6xl">
            A refined virtual consultation for every salon guest.
          </h1>
          <p className="mt-5 text-base leading-7 text-neutral-700 sm:text-lg">
            Upload or capture a portrait, choose a service, and preview a look
            or receive an analysis report before your in-salon consultation.
          </p>
        </div>

        <div className="mt-10 grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
          <div className="space-y-5">
            <Panel title="1. Choose a salon intelligence service" icon={<Sparkles className="h-5 w-5" />}>
              <div className="grid gap-3 sm:grid-cols-2">
                {experienceProducts.map((item) => {
                  const Icon = productIcons[item.id];

                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => {
                        setCategory(item.id);
                        setResult(null);
                        setError(null);
                      }}
                      className={`rounded-lg border p-4 text-left transition ${
                        category === item.id
                          ? "border-[var(--copper)] bg-[#fff2e4] ring-2 ring-[rgba(168,102,61,0.14)]"
                          : "border-[var(--line)] bg-[var(--paper)] hover:border-[var(--copper)]"
                      }`}
                    >
                      <span className="flex items-center gap-3">
                        <span className="grid h-10 w-10 place-items-center rounded-lg bg-white text-[var(--copper-dark)]">
                          <Icon aria-hidden="true" className="h-5 w-5" />
                        </span>
                        <span>
                          <span className="block text-sm font-semibold text-[var(--ink)]">
                            {item.shortName}
                          </span>
                          <span className="mt-1 block text-xs uppercase tracking-[0.18em] text-neutral-500">
                            {item.mode === "try-on" ? "Preview" : "Analysis"}
                          </span>
                        </span>
                      </span>
                    </button>
                  );
                })}
              </div>
            </Panel>

            <Panel title="2. Refine the service" icon={<BadgeCheck className="h-5 w-5" />}>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--copper-dark)]">
                {product.eyebrow}
              </p>
              <h2 className="mt-3 text-2xl font-semibold text-[var(--ink)]">
                {product.name}
              </h2>
              <p className="mt-3 text-sm leading-6 text-neutral-700">
                {product.description}
              </p>

              {options.length > 0 ? (
                <div className="mt-5 grid gap-3">
                  <p className="text-sm font-semibold text-[var(--ink)]">
                    {product.optionLabel}
                  </p>
                  {options.map((option) => (
                    <button
                      key={option.id}
                      type="button"
                      onClick={() => {
                        setSelectedOption(option);
                        setResult(null);
                      }}
                      className={`rounded-lg border bg-[var(--paper)] p-4 text-left transition ${
                        selectedOption?.id === option.id
                          ? "border-[var(--copper)] ring-2 ring-[rgba(168,102,61,0.18)]"
                          : "border-[var(--line)] hover:border-[var(--copper)]"
                      }`}
                    >
                      <span className="flex items-center justify-between gap-3">
                        <span className="font-semibold text-[var(--ink)]">
                          {option.name}
                        </span>
                        {selectedOption?.id === option.id ? (
                          <Check aria-hidden="true" className="h-5 w-5 text-[var(--copper)]" />
                        ) : null}
                      </span>
                      <span className="mt-2 block text-sm leading-6 text-neutral-600">
                        {option.description}
                      </span>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="mt-5 rounded-lg border border-[var(--line)] bg-white/70 p-4 text-sm leading-6 text-neutral-700">
                  This module returns structured analysis for a consultation
                  report. No style selection is required.
                </div>
              )}
            </Panel>
          </div>

          <Panel title="3. Add a portrait and generate" icon={<ImageUp className="h-5 w-5" />} fill>
            <div className="grid gap-5 lg:grid-cols-[0.88fr_1.12fr]">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    type="button"
                    variant={sourceMode === "upload" ? "default" : "secondary"}
                    onClick={() => {
                      setSourceMode("upload");
                      stopCamera();
                    }}
                  >
                    <Upload aria-hidden="true" className="h-5 w-5" />
                    Upload
                  </Button>
                  <Button
                    type="button"
                    variant={sourceMode === "camera" ? "default" : "secondary"}
                    onClick={startCamera}
                  >
                    <Camera aria-hidden="true" className="h-5 w-5" />
                    Camera
                  </Button>
                </div>

                {sourceMode === "upload" ? (
                  <label className="flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-[var(--line)] bg-white/60 p-6 text-center transition hover:border-[var(--copper)]">
                    <Upload aria-hidden="true" className="h-9 w-9 text-[var(--copper)]" />
                    <span className="mt-4 font-semibold text-[var(--ink)]">
                      Upload portrait
                    </span>
                    <span className="mt-2 text-sm leading-6 text-neutral-600">
                      JPG, PNG, or WEBP. Use a clear front-facing image.
                    </span>
                    <input
                      type="file"
                      accept="image/png,image/jpeg,image/webp"
                      className="sr-only"
                      onChange={(event) => {
                        const file = event.target.files?.[0];
                        if (file) updatePhoto(file);
                      }}
                    />
                  </label>
                ) : (
                  <div className="space-y-3">
                    <div className="aspect-square overflow-hidden rounded-lg bg-[var(--ink)]">
                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        className="h-full w-full scale-x-[-1] object-cover"
                      />
                    </div>
                    <Button
                      type="button"
                      className="w-full"
                      disabled={!isCameraActive}
                      onClick={capturePhoto}
                    >
                      <Camera aria-hidden="true" className="h-5 w-5" />
                      Capture
                    </Button>
                  </div>
                )}

                <Button
                  type="button"
                  size="lg"
                  className="w-full"
                  disabled={isProcessing}
                  onClick={runExperience}
                >
                  {isProcessing ? <Spinner /> : <Sparkles aria-hidden="true" className="h-5 w-5" />}
                  {isProcessing
                    ? "Preparing Experience"
                    : product.mode === "try-on"
                      ? "Generate Preview"
                      : "Generate Analysis"}
                </Button>
              </div>

              <div className="min-h-[560px] rounded-lg border border-[var(--line)] bg-[var(--ink)] p-3 text-white">
                <div className="relative flex h-full min-h-[536px] items-center justify-center overflow-hidden rounded-md bg-neutral-950">
                  {isProcessing ? (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.96 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex flex-col items-center px-6 text-center"
                    >
                      <Spinner />
                      <p className="mt-4 font-semibold">Preparing {product.shortName}</p>
                      <p className="mt-2 max-w-sm text-sm leading-6 text-white/62">
                        Your AI salon experience is being prepared by the local
                        self-hosted computer vision backend.
                      </p>
                    </motion.div>
                  ) : result ? (
                    <ResultView
                      beforeSource={previewUrl ?? undefined}
                      comparison={comparison}
                      onComparisonChange={setComparison}
                      productName={product.name}
                      report={result.report}
                      reportItems={reportItems}
                      resultSource={resultSource}
                    />
                  ) : previewUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={previewUrl}
                      alt="Uploaded portrait preview"
                      className="absolute inset-0 h-full w-full object-contain"
                    />
                  ) : (
                    <div className="px-6 text-center">
                      <ImageUp aria-hidden="true" className="mx-auto h-12 w-12 text-white/36" />
                      <p className="mt-4 font-semibold">Your salon preview appears here</p>
                      <p className="mt-2 max-w-sm text-sm leading-6 text-white/58">
                        Add a portrait, choose a service, and generate your
                        preview or consultation report.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {error ? (
              <div className="mt-5 flex gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-800">
                <AlertCircle aria-hidden="true" className="mt-0.5 h-5 w-5 shrink-0" />
                <span>{error}</span>
              </div>
            ) : null}

            {photoFile || result ? (
              <div className="mt-5 flex flex-wrap gap-3">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    setPhotoFile(null);
                    if (previewUrl) URL.revokeObjectURL(previewUrl);
                    setPreviewUrl(null);
                    setResult(null);
                    setError(null);
                  }}
                >
                  <RefreshCcw aria-hidden="true" className="h-5 w-5" />
                  Reset
                </Button>
              </div>
            ) : null}
          </Panel>
        </div>
      </div>
    </section>
  );
}

function ResultView({
  beforeSource,
  comparison,
  onComparisonChange,
  productName,
  report,
  reportItems,
  resultSource
}: {
  beforeSource?: string;
  comparison: number;
  onComparisonChange: (value: number) => void;
  productName: string;
  report?: Record<string, unknown>;
  reportItems: Array<{ label: string; value: string }>;
  resultSource?: string;
}) {
  if (resultSource) {
    return (
      <div className="absolute inset-0">
        {beforeSource ? (
          <div className="absolute inset-0">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={beforeSource}
              alt={`${productName} before`}
              className="absolute inset-0 h-full w-full object-contain"
            />
            <div
              className="absolute inset-0 overflow-hidden"
              style={{ clipPath: `inset(0 ${100 - comparison}% 0 0)` }}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={resultSource}
                alt={`${productName} after`}
                className="h-full w-full object-contain"
              />
            </div>
            <div
              className="pointer-events-none absolute bottom-0 top-0 w-px bg-white/80"
              style={{ left: `${comparison}%` }}
            />
            <input
              type="range"
              min="0"
              max="100"
              value={comparison}
              aria-label="Before and after comparison"
              onChange={(event) => onComparisonChange(Number(event.target.value))}
              className="absolute inset-x-4 bottom-5 h-2 accent-white"
            />
          </div>
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={resultSource}
            alt={`${productName} AI result`}
            className="h-full w-full object-contain"
          />
        )}
        <a
          href={resultSource}
          download="mirrorai-salon-result.png"
          className="absolute right-4 top-4 inline-flex h-11 items-center gap-2 rounded-lg bg-white px-4 text-sm font-semibold text-[var(--ink)]"
        >
          <Download aria-hidden="true" className="h-4 w-4" />
          Save
        </a>
        {report ? (
          <a
            href={jsonDataUrl(report)}
            download="mirrorai-consultation-report.json"
            className="absolute right-4 top-[4.75rem] inline-flex h-11 items-center gap-2 rounded-lg bg-white px-4 text-sm font-semibold text-[var(--ink)]"
          >
            <FileText aria-hidden="true" className="h-4 w-4" />
            JSON
          </a>
        ) : null}
      </div>
    );
  }

  return (
    <div className="w-full max-w-lg px-5 py-8">
      <FileText aria-hidden="true" className="h-10 w-10 text-[#d8a06f]" />
      <p className="mt-4 text-lg font-semibold">{productName} report</p>
      <p className="mt-2 text-sm leading-6 text-white/62">
        Structured provider results are ready for a personalized consultation
        summary inside your salon journey.
      </p>
      {report ? (
        <a
          href={jsonDataUrl(report)}
          download="mirrorai-consultation-report.json"
          className="mt-5 inline-flex h-11 items-center gap-2 rounded-lg bg-white px-4 text-sm font-semibold text-[var(--ink)]"
        >
          <Download aria-hidden="true" className="h-4 w-4" />
          Download JSON
        </a>
      ) : null}
      <div className="mt-6 grid gap-3">
        {reportItems.length > 0 ? (
          reportItems.map((item) => (
            <div
              key={item.label}
              className="rounded-lg border border-white/10 bg-white/[.06] p-4"
            >
              <p className="text-xs uppercase tracking-[0.18em] text-white/45">
                {item.label}
              </p>
              <p className="mt-2 text-sm leading-6 text-white/84">{item.value}</p>
            </div>
          ))
        ) : (
          <div className="rounded-lg border border-white/10 bg-white/[.06] p-4 text-sm leading-6 text-white/70">
            The provider response did not expose simple top-level fields. Open
            the API response in development to map the exact report fields.
          </div>
        )}
      </div>
    </div>
  );
}

function Panel({
  children,
  fill = false,
  icon,
  title
}: {
  children: React.ReactNode;
  fill?: boolean;
  icon: React.ReactNode;
  title: string;
}) {
  return (
    <section
      className={`rounded-lg border border-[var(--line)] bg-[var(--paper)] p-5 sm:p-6 ${
        fill ? "xl:min-h-full" : ""
      }`}
    >
      <div className="mb-5 flex items-center gap-3 text-[var(--ink)]">
        <span className="grid h-10 w-10 place-items-center rounded-lg bg-[#efe3d6] text-[var(--copper-dark)]">
          {icon}
        </span>
        <h2 className="text-lg font-semibold">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function jsonDataUrl(report: Record<string, unknown>) {
  return `data:application/json;charset=utf-8,${encodeURIComponent(
    JSON.stringify(report, null, 2)
  )}`;
}

function buildReportItems(payload: unknown) {
  if (!payload || typeof payload !== "object") return [];

  return Object.entries(payload as Record<string, unknown>)
    .filter(([, value]) => {
      const valueType = typeof value;
      return (
        valueType === "string" ||
        valueType === "number" ||
        valueType === "boolean"
      );
    })
    .slice(0, 6)
    .map(([key, value]) => ({
      label: key.replaceAll("_", " "),
      value: String(value)
    }));
}
