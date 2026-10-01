import http from "node:http";

const PORT = Number(process.env.PORT || 3000);
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const TEXT_MODEL = process.env.OPENAI_TEXT_MODEL || "gpt-5.6-luna";
const IMAGE_MODEL = process.env.OPENAI_IMAGE_MODEL || "gpt-image-2";
const IMAGE_FALLBACK_MODELS = String(process.env.OPENAI_IMAGE_FALLBACK_MODELS || "gpt-image-1")
  .split(",").map(value => value.trim()).filter(Boolean);
const FREE_IMAGE_FALLBACK = String(process.env.FREE_IMAGE_FALLBACK || "true").toLowerCase() !== "false";
const FREE_IMAGE_BASE = "https://image.pollinations.ai/prompt/";
const MAX_BODY_BYTES = 12 * 1024 * 1024;
const OPENAI_TIMEOUT_MS = 110_000;
const FREE_IMAGE_TIMEOUT_MS = 110_000;

if (!OPENAI_API_KEY) console.warn("OPENAI_API_KEY is not configured; free image fallback will be used.");

function json(res, status, body) {
  res.writeHead(status, {"content-type":"application/json; charset=utf-8","cache-control":"no-store","access-control-allow-origin":"*","access-control-allow-methods":"POST,GET,OPTIONS","access-control-allow-headers":"content-type,authorization"});
  res.end(JSON.stringify(body));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0; const chunks = [];
    req.on("data", chunk => { size += chunk.length; if (size > MAX_BODY_BYTES) { reject(new Error("Request body too large.")); req.destroy(); return; } chunks.push(chunk); });
    req.on("end", () => { try { resolve(JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}")); } catch { reject(new Error("Invalid JSON.")); } });
    req.on("error", reject);
  });
}

async function openai(path, options = {}) {
  if (!OPENAI_API_KEY) throw new Error("AI gateway is not configured.");
  const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), OPENAI_TIMEOUT_MS);
  try {
    const response = await fetch("https://api.openai.com" + path, {...options, signal: controller.signal, headers:{authorization:`Bearer ${OPENAI_API_KEY}`,...(options.headers || {})}});
    const text = await response.text(); let data; try { data = JSON.parse(text); } catch { data = {raw:text}; }
    if (!response.ok) { const error = new Error(data?.error?.message || `OpenAI request failed (${response.status}).`); error.status=response.status; error.code=data?.error?.code||null; error.type=data?.error?.type||null; throw error; }
    return data;
  } catch (error) { if (error?.name === "AbortError") throw new Error("AI provider timed out. Please try again."); throw error; }
  finally { clearTimeout(timer); }
}

function responseText(data) {
  if (typeof data.output_text === "string" && data.output_text.trim()) return data.output_text.trim();
  const parts=[]; for (const item of Array.isArray(data.output)?data.output:[]) for (const content of item?.content||[]) if (typeof content?.text==="string") parts.push(content.text);
  return parts.join("\n").trim();
}

function imageBase64(data) {
  const first=Array.isArray(data?.data)?data.data[0]:null; const value=first?.b64_json||first?.base64||data?.image_base64;
  if (typeof value!=="string"||!value) throw new Error("AI provider returned no image."); return value;
}

async function writeText(body) {
  const prompt=String(body.prompt||"").trim(); const language=String(body.language||"Urdu"); if (!prompt) throw new Error("Prompt is required.");
  const data=await openai("/v1/responses",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({model:TEXT_MODEL,input:`Write polished ${language} copy for a graphic design. Preserve the user's meaning.\n\n${prompt}`,max_output_tokens:1200})});
  const text=responseText(data); if(!text) throw new Error("AI returned no text."); return {text};
}

function imageSize(size) {
  if (size === "1536x1024") return [1536,1024];
  if (size === "1024x1536") return [1024,1536];
  return [1024,1024];
}

async function generateFreeImage(body) {
  if (!FREE_IMAGE_FALLBACK) throw new Error("Free image fallback is disabled.");
  const prompt=String(body.prompt||"").trim(); if(!prompt) throw new Error("Prompt is required.");
  const style=String(body.style||"Premium"); const [width,height]=imageSize(body.size);
  const fullPrompt=`${style} professional graphic design for NaqshKaar Designer. ${prompt}. Clean composition, premium lighting, sharp details, no watermark.`;
  const url=FREE_IMAGE_BASE+encodeURIComponent(fullPrompt)+`?model=flux&width=${width}&height=${height}&nologo=true&safe=true`;
  const controller=new AbortController(); const timer=setTimeout(()=>controller.abort(),FREE_IMAGE_TIMEOUT_MS);
  try {
    const response=await fetch(url,{signal:controller.signal,headers:{"user-agent":"NaqshKaar-Designer/1.0"}});
    if(!response.ok) throw new Error(`Free image provider failed (${response.status}).`);
    const type=response.headers.get("content-type")||"";
    if(!type.startsWith("image/")) throw new Error("Free image provider returned a non-image response.");
    return {image_base64:Buffer.from(await response.arrayBuffer()).toString("base64"),provider:"free-image-fallback"};
  } catch(error) {
    if(error?.name==="AbortError") throw new Error("Free image provider timed out. Please try again.");
    throw error;
  } finally { clearTimeout(timer); }
}

async function generateImageWithModel(body, model) {
  const prompt=String(body.prompt||"").trim(); const style=String(body.style||"Premium"); if(!prompt) throw new Error("Prompt is required.");
  const data=await openai("/v1/images/generations",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({model,prompt:`${style} professional graphic design for NaqshKaar Designer. ${prompt}`,size:["1024x1024","1024x1536","1536x1024"].includes(body.size)?body.size:"1024x1024"})});
  return {image_base64:imageBase64(data),provider:"openai"};
}

async function generateImage(body) {
  if (OPENAI_API_KEY) {
    const models=[IMAGE_MODEL,...IMAGE_FALLBACK_MODELS.filter(model=>model!==IMAGE_MODEL)]; let lastError;
    for(const model of models) { try { return await generateImageWithModel(body,model); } catch(error) { lastError=error; } }
    if (!FREE_IMAGE_FALLBACK) throw lastError || new Error("No configured image model is available.");
  }
  return generateFreeImage(body);
}

async function editImage(body, instruction) {
  const input=String(body.image_base64||"").replace(/^data:[^;]+;base64,/,""); if(!input) throw new Error("image_base64 is required.");
  const bytes=Buffer.from(input,"base64"); const form=new FormData(); form.append("model",IMAGE_MODEL); form.append("prompt",instruction); form.append("image[]",new Blob([bytes],{type:"image/png"}),"source.png");
  const data=await openai("/v1/images/edits",{method:"POST",body:form}); return {image_base64:imageBase64(data),provider:"openai"};
}

async function diagnostics() {
  if (OPENAI_API_KEY) {
    const models=[IMAGE_MODEL,...IMAGE_FALLBACK_MODELS.filter(model=>model!==IMAGE_MODEL)]; const available=[]; const unavailable=[];
    for(const model of models) { try { const data=await openai(`/v1/models/${encodeURIComponent(model)}`); available.push(data?.id||model); } catch(error) { unavailable.push({model,error:String(error.message||error),status:error?.status||null,code:error?.code||null}); } }
    if(available.length) return {ok:true,provider:"openai",image_model:available[0],fallback_models:available.slice(1),unavailable,free_fallback_available:FREE_IMAGE_FALLBACK};
  }
  if (FREE_IMAGE_FALLBACK) {
    try {
      const controller=new AbortController(); const timer=setTimeout(()=>controller.abort(),30000);
      const url=FREE_IMAGE_BASE+"NaqshKaar%20diagnostic%20test?model=flux&width=64&height=64&nologo=true&safe=true";
      const response=await fetch(url,{signal:controller.signal,headers:{"user-agent":"NaqshKaar-Designer/1.0"}});
      clearTimeout(timer);
      const type=response.headers.get("content-type")||"";
      if(response.ok && type.startsWith("image/")) return {ok:true,provider:"free-image-fallback",image_model:"flux",openai_configured:Boolean(OPENAI_API_KEY)};
      throw new Error(`free image check returned HTTP ${response.status} ${type}`);
    } catch(error) {
      const e=new Error("No AI image provider is reachable."); e.status=503; e.details={free_fallback:String(error.message||error),openai_configured:Boolean(OPENAI_API_KEY)}; throw e;
    }
  }
  const error=new Error("No AI image provider is configured."); error.status=503; throw error;
}

async function route(path, body) {
  if(path==="/health") return {ok:true,service:"naqshkaar-ai-gateway"};
  if(path==="/diagnostics") return diagnostics();
  if(path==="/write") return writeText(body);
  if(path==="/image") return generateImage(body);
  if(path==="/remove-background") return editImage(body,"Remove the background completely and preserve the main subject cleanly with transparent background. Do not alter the subject.");
  if(path==="/magic-remove") return editImage(body,`Remove the requested object or area while reconstructing the surrounding background naturally. ${String(body.instruction||"")}`);
  if(path==="/enhance") return editImage(body,`Enhance this image professionally: improve clarity, lighting, sharpness and fine details while preserving the original composition, text and subject. ${String(body.instruction||"")}`);
  const error=new Error("Not found."); error.status=404; throw error;
}

export async function handler(req,res) {
  if(req.method==="OPTIONS"){res.writeHead(204,{"access-control-allow-origin":"*","access-control-allow-methods":"POST,GET,OPTIONS","access-control-allow-headers":"content-type,authorization"});return res.end();}
  try { const body=req.method==="POST"?await readBody(req):{}; const rawPath=new URL(req.url,"http://localhost").pathname; const path=rawPath.startsWith("/api/")?rawPath.slice(4):rawPath; const result=await route(path||"/",body); json(res,200,result); }
  catch(error){json(res,error.status||500,{error:String(error.message||error),...(error.code?{code:error.code}:{}),...(error.type?{type:error.type}:{}),...(error.details?{details:error.details}:{})});}
}

if(process.env.VERCEL!=="1"){const server=http.createServer(handler);server.listen(PORT,()=>console.log(`NaqshKaar AI gateway listening on :${PORT}`));}
