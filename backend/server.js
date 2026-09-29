import http from "node:http";

const PORT = Number(process.env.PORT || 3000);
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const TEXT_MODEL = process.env.OPENAI_TEXT_MODEL || "gpt-5.6-luna";
const IMAGE_MODEL = process.env.OPENAI_IMAGE_MODEL || "gpt-image-2";
const MAX_BODY_BYTES = 12 * 1024 * 1024;
const OPENAI_TIMEOUT_MS = 110_000;

if (!OPENAI_API_KEY) {
  console.warn("OPENAI_API_KEY is not configured.");
}

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

async function openai(path, options = {}) {
  if (!OPENAI_API_KEY) throw new Error("AI gateway is not configured.");
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), OPENAI_TIMEOUT_MS);
  try {
    const response = await fetch("https://api.openai.com" + path, {
      ...options,
      signal: controller.signal,
      headers: {
        authorization: `Bearer ${OPENAI_API_KEY}`,
        ...(options.headers || {}),
      },
    });
    const text = await response.text();
    let data;
    try { data = JSON.parse(text); } catch { data = { raw: text }; }
    if (!response.ok) {
      const message = data?.error?.message || `OpenAI request failed (${response.status}).`;
      throw new Error(message);
    }
    return data;
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error("AI provider timed out. Please try again.");
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

function responseText(data) {
  if (typeof data.output_text === "string" && data.output_text.trim()) return data.output_text.trim();
  const output = Array.isArray(data.output) ? data.output : [];
  const parts = [];
  for (const item of output) {
    for (const content of item?.content || []) {
      if (typeof content?.text === "string") parts.push(content.text);
    }
  }
  return parts.join("\n").trim();
}

function imageBase64(data) {
  const first = Array.isArray(data?.data) ? data.data[0] : null;
  const value = first?.b64_json || first?.base64 || data?.image_base64;
  if (typeof value !== "string" || !value) throw new Error("OpenAI returned no image.");
  return value;
}

async function writeText(body) {
  const prompt = String(body.prompt || "").trim();
  const language = String(body.language || "Urdu");
  if (!prompt) throw new Error("Prompt is required.");
  const data = await openai("/v1/responses", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      model: TEXT_MODEL,
      input: `Write polished ${language} copy for a graphic design. Preserve the user's meaning.\n\n${prompt}`,
      max_output_tokens: 1200,
    }),
  });
  const text = responseText(data);
  if (!text) throw new Error("AI returned no text.");
  return { text };
}

async function generateImage(body) {
  const prompt = String(body.prompt || "").trim();
  const style = String(body.style || "Premium");
  if (!prompt) throw new Error("Prompt is required.");
  const data = await openai("/v1/images/generations", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      model: IMAGE_MODEL,
      prompt: `${style} professional graphic design for NaqshKaar Designer. ${prompt}`,
      size: ["1024x1024", "1024x1536", "1536x1024"].includes(body.size) ? body.size : "1024x1024",
    }),
  });
  return { image_base64: imageBase64(data) };
}

async function editImage(body, instruction) {
  const input = String(body.image_base64 || "").replace(/^data:[^;]+;base64,/, "");
  if (!input) throw new Error("image_base64 is required.");

  const bytes = Buffer.from(input, "base64");
  const form = new FormData();
  form.append("model", IMAGE_MODEL);
  form.append("prompt", instruction);
  form.append("image[]", new Blob([bytes], { type: "image/png" }), "source.png");

  const data = await openai("/v1/images/edits", {
    method: "POST",
    body: form,
  });
  return { image_base64: imageBase64(data) };
}

async function diagnostics() {
  const data = await openai(`/v1/models/${encodeURIComponent(IMAGE_MODEL)}`);
  return {
    ok: true,
    provider: "openai",
    image_model: data?.id || IMAGE_MODEL,
  };
}

async function route(path, body) {
  if (path === "/health") return { ok: true, service: "naqshkaar-ai-gateway" };
  if (path === "/diagnostics") return diagnostics();
  if (path === "/write") return writeText(body);
  if (path === "/image") return generateImage(body);
  if (path === "/remove-background") return editImage(body, "Remove the background completely and preserve the main subject cleanly with transparent background. Do not alter the subject.");
  if (path === "/magic-remove") return editImage(body, `Remove the requested object or area while reconstructing the surrounding background naturally. ${String(body.instruction || "")}`);
  if (path === "/enhance") return editImage(body, `Enhance this image professionally: improve clarity, lighting, sharpness and fine details while preserving the original composition, text and subject. ${String(body.instruction || "")}`);
  const error = new Error("Not found.");
  error.status = 404;
  throw error;
}

export async function handler(req, res) {
  if (req.method === "OPTIONS") {
    res.writeHead(204, { "access-control-allow-origin": "*", "access-control-allow-methods": "POST,GET,OPTIONS", "access-control-allow-headers": "content-type,authorization" });
    return res.end();
  }
  try {
    const body = req.method === "POST" ? await readBody(req) : {};
    const rawPath = new URL(req.url, "http://localhost").pathname;
    const path = rawPath.startsWith("/api/") ? rawPath.slice(4) : rawPath;
    const result = await route(path || "/", body);
    json(res, 200, result);
  } catch (error) {
    json(res, error.status || 500, { error: String(error.message || error) });
  }
}

if (process.env.VERCEL !== "1") {
  const server = http.createServer(handler);
  server.listen(PORT, () => console.log(`NaqshKaar AI gateway listening on :${PORT}`));
}
