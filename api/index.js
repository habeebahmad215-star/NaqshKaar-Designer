import {deflateSync} from "node:zlib";

function send(res, status, body) {
  res.statusCode = status;
  res.setHeader("content-type", "application/json; charset=utf-8");
  res.setHeader("cache-control", "no-store");
  res.setHeader("access-control-allow-origin", "*");
  res.setHeader("access-control-allow-methods", "GET,POST,OPTIONS");
  res.setHeader("access-control-allow-headers", "content-type,authorization");
  res.end(JSON.stringify(body));
}

function ratioFor(size) {
  if (size === "1536x1024") return "16:9";
  if (size === "1024x1536") return "9:16";
  return "1:1";
}

function dimensionsFor(size) {
  if (size === "1536x1024") return [1536, 1024];
  if (size === "1024x1536") return [1024, 1536];
  return [1024, 1024];
}

function extractImage(data) {
  if (data && data.output_image && typeof data.output_image.data === "string") {
    return data.output_image.data;
  }
  const steps = data && Array.isArray(data.steps) ? data.steps : [];
  for (const step of steps) {
    const content = step && Array.isArray(step.content) ? step.content : [];
    for (const item of content) {
      if (item && item.type === "image" && typeof item.data === "string") {
        return item.data;
      }
    }
  }
  throw new Error("Gemini returned no image data.");
}

function promptFor(body) {
  const prompt = String(body && body.prompt || "").trim();
  if (!prompt) throw new Error("Prompt is required.");
  const style = String(body && body.style || "Premium").trim();
  return style + " professional graphic design for NaqshKaar Designer. " + prompt +
    "\n\nCreate a polished production-ready commercial composition with strong visual hierarchy, balanced spacing, premium lighting, depth, crisp details and clean edges. Use an elegant Urdu/Islamic/modern visual language when appropriate. Leave intentional clean space for editable headline text. Do not invent tiny unreadable paragraphs, fake logos, random gibberish or watermarks.";
}

async function requestGeminiImage(body, model) {
  const key = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  if (!key) throw new Error("Gemini API is not configured on the production server.");

  const size = String(body && body.size || "1024x1024");
  const response = await fetch("https://generativelanguage.googleapis.com/v1beta/interactions", {
    method: "POST",
    headers: {
      "x-goog-api-key": key,
      "content-type": "application/json"
    },
    body: JSON.stringify({
      model,
      input: promptFor(body),
      response_format: {
        type: "image",
        mime_type: "image/jpeg",
        aspect_ratio: ratioFor(size),
        image_size: "1K"
      }
    })
  });

  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch (_) {
    const error = new Error("Gemini returned invalid JSON (HTTP " + response.status + ").");
    error.status = response.status;
    throw error;
  }

  if (!response.ok) {
    const providerMessage = data && data.error && data.error.message;
    const error = new Error(providerMessage || "Gemini image request failed (HTTP " + response.status + ").");
    error.status = response.status;
    throw error;
  }

  return {
    image_base64: extractImage(data),
    provider: "gemini",
    image_model: model
  };
}

function crc32(buffer) {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc ^= byte;
    for (let i = 0; i < 8; i++) {
      crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function pngChunk(type, data) {
  const typeBytes = Buffer.from(type, "ascii");
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length, 0);
  const checksum = Buffer.alloc(4);
  checksum.writeUInt32BE(crc32(Buffer.concat([typeBytes, data])), 0);
  return Buffer.concat([length, typeBytes, data, checksum]);
}

function smartTemplatePng(body) {
  const [width, height] = dimensionsFor(String(body && body.size || "1024x1024"));
  const style = String(body && body.style || "Premium").toLowerCase();
  const prompt = String(body && body.prompt || "").toLowerCase();
  let palette;
  if (style.includes("islamic") || prompt.includes("ramadan") || prompt.includes("quran") || prompt.includes("islam")) {
    palette = [[9, 55, 43], [24, 112, 77], [190, 154, 65]];
  } else if (style.includes("luxury")) {
    palette = [[8, 10, 16], [48, 42, 31], [205, 169, 77]];
  } else if (style.includes("school") || prompt.includes("admission") || prompt.includes("school")) {
    palette = [[12, 54, 96], [37, 119, 174], [240, 184, 62]];
  } else if (style.includes("youtube") || prompt.includes("thumbnail")) {
    palette = [[16, 18, 25], [91, 26, 54], [224, 58, 69]];
  } else if (style.includes("minimal")) {
    palette = [[238, 241, 246], [196, 208, 223], [74, 88, 110]];
  } else {
    palette = [[19, 27, 63], [74, 34, 126], [70, 148, 190]];
  }

  const raw = Buffer.alloc((width * 3 + 1) * height);
  let offset = 0;
  const cx = width * 0.5;
  const cy = height * 0.46;
  const maxD = Math.hypot(cx, cy);
  const dark = palette[0];
  const mid = palette[1];
  const accent = palette[2];

  for (let y = 0; y < height; y++) {
    raw[offset++] = 0;
    for (let x = 0; x < width; x++) {
      const nx = x / Math.max(1, width - 1);
      const ny = y / Math.max(1, height - 1);
      const d = Math.hypot(x - cx, y - cy) / maxD;
      const glow = Math.max(0, 1 - d) ** 2;
      const diagonal = Math.max(0, Math.sin((x + y) * 0.008));
      const t = Math.min(1, Math.max(0, 0.48 * nx + 0.32 * ny + 0.20 * glow));
      let r = dark[0] * (1 - t) + mid[0] * t;
      let g = dark[1] * (1 - t) + mid[1] * t;
      let b = dark[2] * (1 - t) + mid[2] * t;
      r += accent[0] * glow * 0.34 + accent[0] * diagonal * 0.025;
      g += accent[1] * glow * 0.34 + accent[1] * diagonal * 0.025;
      b += accent[2] * glow * 0.34 + accent[2] * diagonal * 0.025;

      const border = Math.min(x, y, width - 1 - x, height - 1 - y);
      if (border < Math.max(4, Math.round(Math.min(width, height) * 0.012))) {
        r = r * 0.72 + accent[0] * 0.28;
        g = g * 0.72 + accent[1] * 0.28;
        b = b * 0.72 + accent[2] * 0.28;
      }

      const rx = x - cx;
      const ry = y - cy;
      const radius = Math.hypot(rx, ry);
      const ring = Math.abs((radius % Math.max(80, Math.min(width, height) * 0.14)) - Math.max(80, Math.min(width, height) * 0.07));
      if (ring < 2.2) {
        r = r * 0.45 + accent[0] * 0.55;
        g = g * 0.45 + accent[1] * 0.55;
        b = b * 0.45 + accent[2] * 0.55;
      }

      const lineA = Math.abs((rx * 0.707 + ry * 0.707) % Math.max(90, Math.min(width, height) * 0.18));
      const lineB = Math.abs((rx * 0.707 - ry * 0.707) % Math.max(90, Math.min(width, height) * 0.18));
      if (lineA < 1.2 || lineB < 1.2) {
        r = r * 0.60 + accent[0] * 0.40;
        g = g * 0.60 + accent[1] * 0.40;
        b = b * 0.60 + accent[2] * 0.40;
      }

      raw[offset++] = Math.max(0, Math.min(255, Math.round(r)));
      raw[offset++] = Math.max(0, Math.min(255, Math.round(g)));
      raw[offset++] = Math.max(0, Math.min(255, Math.round(b)));
    }
  }

  const signature = Buffer.from([
    137, 80, 78, 71, 13, 10, 26, 10
  ]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 2;
  ihdr[10] = 0;
  ihdr[11] = 0;
  ihdr[12] = 0;
  const idat = deflateSync(raw, {level: 6});
  const png = Buffer.concat([
    signature,
    pngChunk("IHDR", ihdr),
    pngChunk("IDAT", idat),
    pngChunk("IEND", Buffer.alloc(0)),
  ]);
  return png.toString("base64");
}

async function generateSmartTemplate(body, reason) {
  return {
    image_base64: smartTemplatePng(body),
    provider: "smart-template-fallback",
    image_model: "NaqshKaar Premium Template Engine",
    provider_message: reason
      ? "Gemini unavailable; premium local template fallback used."
      : "Premium template engine ready.",
  };
}

async function generateImage(body) {
  const primary = process.env.GEMINI_IMAGE_MODEL || "gemini-3.1-flash-image";
  const models = [primary, "gemini-3.1-flash-lite-image"]
    .filter((model, index, list) => model && list.indexOf(model) === index);

  let lastError;
  const key = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  if (key) {
    for (const model of models) {
      try {
        return await requestGeminiImage(body, model);
      } catch (error) {
        lastError = error;
        console.error("Gemini image model unavailable:", model, error);
      }
    }
  }

  return generateSmartTemplate(body, lastError ? String(lastError.message || lastError) : null);
}

export default async function apiHandler(req, res) {
  if (req.method === "OPTIONS") {
    res.statusCode = 204;
    res.setHeader("access-control-allow-origin", "*");
    res.setHeader("access-control-allow-methods", "GET,POST,OPTIONS");
    res.setHeader("access-control-allow-headers", "content-type,authorization");
    return res.end();
  }

  const path = new URL(req.url || "/", "http://localhost").pathname;

  if (path === "/api/health" || path === "/health") {
    return send(res, 200, {
      ok: true,
      service: "naqshkaar-ai-gateway",
      runtime: process.version
    });
  }

  try {
    if (path === "/api/diagnostics" || path === "/diagnostics") {
      const key = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
      return send(res, 200, {
        ok: true,
        provider: key ? "gemini + smart-template-fallback" : "smart-template-fallback",
        image_model: process.env.GEMINI_IMAGE_MODEL || "gemini-3.1-flash-image",
        failover_model: "gemini-3.1-flash-lite-image",
        key_configured: Boolean(key),
        fallback_available: true
      });
    }

    if (path === "/api/image" || path === "/image") {
      let body = req.body;
      if (typeof body === "string") body = JSON.parse(body || "{}");
      if (!body || typeof body !== "object") body = {};
      return send(res, 200, await generateImage(body));
    }

    return send(res, 404, {error: "Not found."});
  } catch (error) {
    console.error("NaqshKaar API error:", error);
    return send(res, Number(error && error.status) || 500, {
      error: String(error && error.message || error),
      runtime: process.version
    });
  }
}
