function json(res, status, body) {
  res.statusCode = status;
  res.setHeader("content-type", "application/json; charset=utf-8");
  res.setHeader("cache-control", "no-store");
  res.setHeader("access-control-allow-origin", "*");
  res.setHeader("access-control-allow-methods", "POST,OPTIONS");
  res.setHeader("access-control-allow-headers", "content-type,authorization");
  res.end(JSON.stringify(body));
}
function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = []; let size = 0;
    req.on("data", chunk => { size += chunk.length; if (size > 12 * 1024 * 1024) { reject(new Error("Request body too large.")); req.destroy(); return; } chunks.push(chunk); });
    req.on("end", () => { try { resolve(JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}")); } catch { reject(new Error("Invalid JSON.")); } });
    req.on("error", reject);
  });
}
function extractImage(data) {
  if (typeof data?.output_image?.data === "string") return data.output_image.data;
  for (const step of Array.isArray(data?.steps) ? data.steps : []) for (const content of Array.isArray(step?.content) ? step.content : []) if (content?.type === "image" && typeof content?.data === "string") return content.data;
  for (const item of Array.isArray(data?.outputs) ? data.outputs : []) { if (typeof item?.image?.data === "string") return item.image.data; if (typeof item?.output_image?.data === "string") return item.output_image.data; }
  throw new Error("Gemini returned no image data.");
}
export default async function handler(req, res) {
  if (req.method === "OPTIONS") { res.writeHead(204); return res.end(); }
  if (req.method !== "POST") return json(res, 405, {error: "POST is required."});
  try {
    const body = await readBody(req);
    const key = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
    if (!key) return json(res, 503, {error: "Gemini API is not configured."});
    const prompt = String(body.prompt || "").trim();
    if (!prompt) return json(res, 400, {error: "Prompt is required."});
    const style = String(body.style || "Premium");
    const size = String(body.size || "1024x1024");
    const aspectRatio = size === "1536x1024" ? "16:9" : size === "1024x1536" ? "9:16" : "1:1";
    const model = process.env.GEMINI_IMAGE_MODEL || "gemini-3.1-flash-image";
    const designPrompt = style + " professional graphic design for NaqshKaar Designer. " + prompt + "\n\nCreate a polished production-ready commercial composition with strong visual hierarchy, balanced spacing, premium lighting, depth, crisp details and clean edges. Use an elegant Urdu/Islamic/modern visual language when appropriate. Leave intentional clean space for editable headline text that NaqshKaar will overlay separately. Do not invent tiny unreadable paragraphs, fake logos, random gibberish or watermarks.";
    const upstream = await fetch("https://generativelanguage.googleapis.com/v1beta/interactions", { method: "POST", headers: {"x-goog-api-key": key, "content-type": "application/json"}, body: JSON.stringify({model, input: designPrompt, response_format: {type: "image", mime_type: "image/jpeg", aspect_ratio: aspectRatio, image_size: "1K"}}) });
    const raw = await upstream.text();
    let data; try { data = JSON.parse(raw); } catch { data = {raw}; }
    if (!upstream.ok) return json(res, upstream.status, {error: data?.error?.message || ("Gemini request failed (" + upstream.status + ").")});
    return json(res, 200, {image_base64: extractImage(data), provider: "gemini", image_model: model});
  } catch (error) { console.error("NaqshKaar /api/image failure:", error); return json(res, 500, {error: String(error?.message || error)}); }
}