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

function extractImage(data) {
  if (typeof data?.output_image?.data === "string") return data.output_image.data;
  for (const step of Array.isArray(data?.steps) ? data.steps : []) {
    for (const item of Array.isArray(step?.content) ? step.content : []) {
      if (item?.type === "image" && typeof item.data === "string") return item.data;
    }
  }
  throw new Error("Gemini returned no image data.");
}

function promptFor(body) {
  const prompt = String(body?.prompt || "").trim();
  if (!prompt) throw new Error("Prompt is required.");
  const style = String(body?.style || "Premium").trim();
  return `${style} professional graphic design for NaqshKaar Designer. ${prompt}

Create a polished production-ready commercial composition with strong visual hierarchy, balanced spacing, premium lighting, depth, crisp details and clean edges. Use an elegant Urdu/Islamic/modern visual language when appropriate. Leave intentional clean space for editable headline text. Do not invent tiny unreadable paragraphs, fake logos, random gibberish or watermarks.`;
}

async function generateImage(body) {
  const key = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  if (!key) throw new Error("Gemini API is not configured on the production server.");

  const model = process.env.GEMINI_IMAGE_MODEL || "gemini-3.1-flash-image";
  const size = String(body?.size || "1024x1024");
  const response = await fetch("https://generativelanguage.googleapis.com/v1beta/interactions", {
    method: "POST",
    headers: {"x-goog-api-key": key, "content-type": "application/json"},
    body: JSON.stringify({
      model,
      input: promptFor(body),
      response_format: {
        type: "image",
        mime_type: "image/jpeg",
        aspect_ratio: ratioFor(size),
        image_size: "1K",
      },
    }),
  });

  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(`Gemini returned invalid JSON (HTTP ${response.status}).`);
  }
  if (!response.ok) {
    throw new Error(data?.error?.message || `Gemini image request failed (HTTP ${response.status}).`);
  }

  return {
    image_base64: extractImage(data),
    provider: "gemini",
    image_model: model,
  };
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
    return send(res, 200, {ok: true, service: "naqshkaar-ai-gateway", runtime: process.version});
  }

  try {
    if (path === "/api/image" || path === "/image") {
      const chunks = [];
      for await (const chunk of req) chunks.push(chunk);
      const body = JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}");
      return send(res, 200, await generateImage(body));
    }

    if (path === "/api/diagnostics" || path === "/diagnostics") {
      const key = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
      return send(res, 200, {
        ok: Boolean(key),
        provider: "gemini",
        image_model: process.env.GEMINI_IMAGE_MODEL || "gemini-3.1-flash-image",
        key_configured: Boolean(key),
      });
    }

    const {handler} = await import("../backend/server.js");
    return await handler(req, res);
  } catch (error) {
    console.error("NaqshKaar API error:", error);
    return send(res, Number(error?.status) || 500, {
      error: String(error?.message || error),
      runtime: process.version,
    });
  }
}
