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

async function generateImage(body) {
  const primary = process.env.GEMINI_IMAGE_MODEL || "gemini-3.1-flash-image";
  const models = [primary, "gemini-3.1-flash-lite-image"]
    .filter((model, index, list) => model && list.indexOf(model) === index);

  let lastError;
  for (const model of models) {
    try {
      return await requestGeminiImage(body, model);
    } catch (error) {
      lastError = error;
      console.error("Gemini image model unavailable:", model, error);
    }
  }

  throw lastError || new Error("No Gemini image model is available.");
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
        ok: Boolean(key),
        provider: "gemini",
        image_model: process.env.GEMINI_IMAGE_MODEL || "gemini-3.1-flash-image",
        failover_model: "gemini-3.1-flash-lite-image",
        key_configured: Boolean(key)
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
