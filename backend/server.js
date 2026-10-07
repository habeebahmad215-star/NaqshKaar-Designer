import http from "node:http";

const PORT = Number(process.env.PORT || 3000);
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;

const TEXT_MODEL = process.env.OPENAI_TEXT_MODEL || "gpt-5.6-luna";
const OPENAI_IMAGE_MODEL = process.env.OPENAI_IMAGE_MODEL || "gpt-image-2";
const OPENAI_IMAGE_FALLBACK_MODELS = String(process.env.OPENAI_IMAGE_FALLBACK_MODELS || "gpt-image-1")
  .split(",").map(value => value.trim()).filter(Boolean);

const GEMINI_IMAGE_MODEL = process.env.GEMINI_IMAGE_MODEL || "gemini-3.1-flash-image";
const GEMINI_PRO_IMAGE_MODEL = process.env.GEMINI_PRO_IMAGE_MODEL || "gemini-3-pro-image";
const GEMINI_IMAGE_SIZE = String(process.env.GEMINI_IMAGE_SIZE || "1K").toUpperCase();

const FREE_IMAGE_FALLBACK =
  String(process.env.FREE_IMAGE_FALLBACK || "true").toLowerCase() !== "false";
const FREE_IMAGE_BASE = "https://image.pollinations.ai/prompt/";

const MAX_BODY_BYTES = 12 * 1024 * 1024;
const PROVIDER_TIMEOUT_MS = 110_000;
const FREE_IMAGE_TIMEOUT_MS = 110_000;

function json(res, status, body) {
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "POST,GET,OPTIONS",
    "access-control-allow-headers": "content-type,authorization",
  });
  res.end(JSON.stringify(body));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on("data", chunk => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        reject(new Error("Request body too large."));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}"));
      } catch {
        reject(new Error("Invalid JSON."));
      }
    });
    req.on("error", reject);
  });
}

async function providerFetch(baseUrl, path, options, authHeaders, label) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), PROVIDER_TIMEOUT_MS);
  try {
    const response = await fetch(baseUrl + path, {
      ...options,
      signal: controller.signal,
      headers: {...authHeaders, ...(options?.headers || {})},
    });
    const text = await response.text();
    let data;
    try { data = JSON.parse(text); } catch { data = {raw: text}; }
    if (!response.ok) {
      const error = new Error(
        data?.error?.message ||
        data?.error?.status ||
        `${label} request failed (${response.status}).`,
      );
      error.status = response.status;
      error.code = data?.error?.status || data?.error?.code || null;
      throw error;
    }
    return data;
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error(`${label} request timed out. Please try again.`);
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

async function openai(path, options = {}) {
  if (!OPENAI_API_KEY) throw new Error("OpenAI API is not configured.");
  return providerFetch(
    "https://api.openai.com",
    path,
    options,
    {authorization: `Bearer ${OPENAI_API_KEY}`},
    "OpenAI",
  );
}

async function gemini(path, options = {}) {
  if (!GEMINI_API_KEY) throw new Error("Gemini API is not configured.");
  return providerFetch(
    "https://generativelanguage.googleapis.com/v1beta",
    path,
    options,
    {"x-goog-api-key": GEMINI_API_KEY, "content-type": "application/json"},
    "Gemini",
  );
}

function responseText(data) {
  if (typeof data.output_text === "string" && data.output_text.trim()) {
    return data.output_text.trim();
  }
  const parts = [];
  for (const item of Array.isArray(data.output) ? data.output : []) {
    for (const content of item?.content || []) {
      if (typeof content?.text === "string") parts.push(content.text);
    }
  }
  return parts.join("\n").trim();
}

function imageBase64(data) {
  const first = Array.isArray(data?.data) ? data.data[0] : null;
  const value = first?.b64_json || first?.base64 || data?.image_base64;
  if (typeof value !== "string" || !value) {
    throw new Error("AI provider returned no image.");
  }
  return value;
}

function extractGeminiImage(data) {
  if (typeof data?.output_image?.data === "string") return data.output_image.data;
  for (const step of Array.isArray(data?.steps) ? data.steps : []) {
    for (const content of Array.isArray(step?.content) ? step.content : []) {
      if (content?.type === "image" && typeof content?.data === "string") {
        return content.data;
      }
    }
  }
  for (const item of Array.isArray(data?.outputs) ? data.outputs : []) {
    if (typeof item?.image?.data === "string") return item.image.data;
    if (typeof item?.output_image?.data === "string") return item.output_image.data;
  }
  throw new Error("Gemini returned no image data.");
}

function geminiAspectRatio(size) {
  if (size === "1536x1024") return "16:9";
  if (size === "1024x1536") return "9:16";
  return "1:1";
}

function imageSize(size) {
  if (size === "1536x1024") return [1536, 1024];
  if (size === "1024x1536") return [1024, 1536];
  return [1024, 1024];
}

async function writeText(body) {
  const prompt = String(body.prompt || "").trim();
  const language = String(body.language || "Urdu");
  if (!prompt) throw new Error("Prompt is required.");

  const data = await openai("/v1/responses", {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify({
      model: TEXT_MODEL,
      input: `Write polished ${language} copy for a graphic design. Preserve the user's meaning.\n\n${prompt}`,
      max_output_tokens: 1200,
    }),
  });
  const text = responseText(data);
  if (!text) throw new Error("AI returned no text.");
  return {text};
}

function buildImagePrompt(body) {
  const prompt = String(body.prompt || "").trim();
  const style = String(body.style || "Premium");
  if (!prompt) throw new Error("Prompt is required.");
  return `${style} professional graphic design for NaqshKaar Designer. ${prompt}

Create a polished production-ready commercial composition with strong visual hierarchy, balanced spacing, premium lighting, depth, crisp details and clean edges. Use an elegant Urdu/Islamic/modern visual language when appropriate. Leave intentional clean space for editable headline text that NaqshKaar will overlay separately. Do not invent tiny unreadable paragraphs, fake logos, random gibberish or watermarks.`;
}

async function generateGeminiImage(body, model = GEMINI_IMAGE_MODEL) {
  const data = await gemini("/interactions", {
    method: "POST",
    body: JSON.stringify({
      model,
      input: buildImagePrompt(body),
      response_format: {
        type: "image",
        mime_type: "image/jpeg",
        aspect_ratio: geminiAspectRatio(body.size),
        image_size: GEMINI_IMAGE_SIZE,
      },
    }),
  });
  return {
    image_base64: extractGeminiImage(data),
    provider: "gemini",
    image_model: model,
  };
}

async function editGeminiImage(body, instruction) {
  const input = String(body.image_base64 || "").replace(/^data:[^;]+;base64,/, "");
  if (!input) throw new Error("image_base64 is required.");

  const data = await gemini("/interactions", {
    method: "POST",
    body: JSON.stringify({
      model: GEMINI_IMAGE_MODEL,
      input: [
        {type: "image", mime_type: "image/png", data: input},
        {type: "text", text: instruction},
      ],
      response_format: {
        type: "image",
        mime_type: "image/jpeg",
        image_size: GEMINI_IMAGE_SIZE,
      },
    }),
  });
  return {
    image_base64: extractGeminiImage(data),
    provider: "gemini",
    image_model: GEMINI_IMAGE_MODEL,
  };
}

async function generateFreeImage(body) {
  if (!FREE_IMAGE_FALLBACK) throw new Error("Free image fallback is disabled.");
  const prompt = String(body.prompt || "").trim();
  if (!prompt) throw new Error("Prompt is required.");

  const style = String(body.style || "Premium");
  const [width, height] = imageSize(body.size);
  const fullPrompt =
    `${style} professional graphic design for NaqshKaar Designer. ${prompt}. Clean composition, premium lighting, sharp details, no watermark.`;
  const url =
    FREE_IMAGE_BASE + encodeURIComponent(fullPrompt) +
    `?model=flux&width=${width}&height=${height}&nologo=true&safe=true`;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FREE_IMAGE_TIMEOUT_MS);
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {"user-agent": "NaqshKaar-Designer/1.0"},
    });
    if (!response.ok) throw new Error(`Free image provider failed (${response.status}).`);
    const type = response.headers.get("content-type") || "";
    if (!type.startsWith("image/")) {
      throw new Error("Free image provider returned a non-image response.");
    }
    return {
      image_base64: Buffer.from(await response.arrayBuffer()).toString("base64"),
      provider: "free-image-fallback",
      image_model: "flux",
    };
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error("Free image provider timed out. Please try again.");
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

async function generateOpenAIImage(body, model) {
  const data = await openai("/v1/images/generations", {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify({
      model,
      prompt: buildImagePrompt(body),
      size: ["1024x1024", "1024x1536", "1536x1024"].includes(body.size)
        ? body.size
        : "1024x1024",
    }),
  });
  return {
    image_base64: imageBase64(data),
    provider: "openai",
    image_model: model,
  };
}

async function editOpenAIImage(body, instruction) {
  const input = String(body.image_base64 || "").replace(/^data:[^;]+;base64,/, "");
  if (!input) throw new Error("image_base64 is required.");
  const bytes = Buffer.from(input, "base64");
  const form = new FormData();
  form.append("model", OPENAI_IMAGE_MODEL);
  form.append("prompt", instruction);
  form.append("image[]", new Blob([bytes], {type: "image/png"}), "source.png");
  const data = await openai("/v1/images/edits", {method: "POST", body: form});
  return {image_base64: imageBase64(data), provider: "openai", image_model: OPENAI_IMAGE_MODEL};
}

async function generateImage(body) {
  let lastError;

  if (GEMINI_API_KEY) {
    try {
      return await generateGeminiImage(body);
    } catch (error) {
      lastError = error;
      if (GEMINI_PRO_IMAGE_MODEL !== GEMINI_IMAGE_MODEL) {
        try {
          return await generateGeminiImage(body, GEMINI_PRO_IMAGE_MODEL);
        } catch (error2) {
          lastError = error2;
        }
      }
    }
  }

  if (OPENAI_API_KEY) {
    const models = [
      OPENAI_IMAGE_MODEL,
      ...OPENAI_IMAGE_FALLBACK_MODELS.filter(model => model !== OPENAI_IMAGE_MODEL),
    ];
    for (const model of models) {
      try {
        return await generateOpenAIImage(body, model);
      } catch (error) {
        lastError = error;
      }
    }
  }

  if (FREE_IMAGE_FALLBACK) return generateFreeImage(body);
  throw lastError || new Error("No configured AI image provider is available.");
}

async function editImage(body, instruction) {
  let lastError;

  if (GEMINI_API_KEY) {
    try {
      return await editGeminiImage(body, instruction);
    } catch (error) {
      lastError = error;
    }
  }

  if (OPENAI_API_KEY) {
    try {
      return await editOpenAIImage(body, instruction);
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError || new Error("No AI image editing provider is configured.");
}

async function diagnostics() {
  const unavailable = [];

  if (GEMINI_API_KEY) {
    try {
      const data = await gemini(`/models/${encodeURIComponent(GEMINI_IMAGE_MODEL)}`);
      return {
        ok: true,
        provider: "gemini",
        image_model: data?.name || GEMINI_IMAGE_MODEL,
        openai_configured: Boolean(OPENAI_API_KEY),
        free_fallback_available: FREE_IMAGE_FALLBACK,
      };
    } catch (error) {
      unavailable.push({
        provider: "gemini",
        model: GEMINI_IMAGE_MODEL,
        error: String(error.message || error),
        status: error?.status || null,
      });
    }
  }

  if (OPENAI_API_KEY) {
    const models = [
      OPENAI_IMAGE_MODEL,
      ...OPENAI_IMAGE_FALLBACK_MODELS.filter(model => model !== OPENAI_IMAGE_MODEL),
    ];
    for (const model of models) {
      try {
        const data = await openai(`/v1/models/${encodeURIComponent(model)}`);
        return {
          ok: true,
          provider: "openai",
          image_model: data?.id || model,
          gemini_configured: Boolean(GEMINI_API_KEY),
          free_fallback_available: FREE_IMAGE_FALLBACK,
          unavailable,
        };
      } catch (error) {
        unavailable.push({
          provider: "openai",
          model,
          error: String(error.message || error),
          status: error?.status || null,
        });
      }
    }
  }

  if (FREE_IMAGE_FALLBACK) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 30_000);
      const url =
        FREE_IMAGE_BASE +
        "NaqshKaar%20diagnostic%20test?model=flux&width=64&height=64&nologo=true&safe=true";
      const response = await fetch(url, {
        signal: controller.signal,
        headers: {"user-agent": "NaqshKaar-Designer/1.0"},
      });
      clearTimeout(timer);
      const type = response.headers.get("content-type") || "";
      if (response.ok && type.startsWith("image/")) {
        return {
          ok: true,
          provider: "free-image-fallback",
          image_model: "flux",
          gemini_configured: Boolean(GEMINI_API_KEY),
          openai_configured: Boolean(OPENAI_API_KEY),
          unavailable,
        };
      }
    } catch (error) {
      unavailable.push({
        provider: "free-image-fallback",
        error: String(error.message || error),
      });
    }
  }

  const error = new Error("No AI image provider is reachable.");
  error.status = 503;
  error.details = {
    gemini_configured: Boolean(GEMINI_API_KEY),
    openai_configured: Boolean(OPENAI_API_KEY),
    unavailable,
  };
  throw error;
}

async function route(path, body) {
  if (path === "/health") return {ok: true, service: "naqshkaar-ai-gateway"};
  if (path === "/diagnostics") return diagnostics();
  if (path === "/write") return writeText(body);
  if (path === "/image") return generateImage(body);
  if (path === "/remove-background") {
    return editImage(body, "Remove the background completely. Preserve the main subject cleanly with a transparent-looking isolated result. Do not alter the subject.");
  }
  if (path === "/magic-remove") {
    return editImage(
      body,
      `Remove the requested object or area while reconstructing the surrounding background naturally. ${String(body.instruction || "")}`,
    );
  }
  if (path === "/enhance") {
    return editImage(
      body,
      `Enhance this image professionally: improve clarity, lighting, sharpness and fine details while preserving the original composition, text and subject. ${String(body.instruction || "")}`,
    );
  }
  const error = new Error("Not found.");
  error.status = 404;
  throw error;
}

export async function handler(req, res) {
  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "POST,GET,OPTIONS",
      "access-control-allow-headers": "content-type,authorization",
    });
    return res.end();
  }

  try {
    const body = req.method === "POST" ? await readBody(req) : {};
    const rawPath = new URL(req.url, "http://localhost").pathname;
    const path = rawPath.startsWith("/api/") ? rawPath.slice(4) : rawPath;
    const result = await route(path || "/", body);
    json(res, 200, result);
  } catch (error) {
    json(res, error.status || 500, {
      error: String(error.message || error),
      ...(error.code ? {code: error.code} : {}),
      ...(error.details ? {details: error.details} : {}),
    });
  }
}

if (process.env.VERCEL !== "1") {
  const server = http.createServer(handler);
  server.listen(PORT, () => console.log(`NaqshKaar AI gateway listening on :${PORT}`));
}
