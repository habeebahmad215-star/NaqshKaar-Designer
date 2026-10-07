function writeJson(res, status, body) {
  res.statusCode = status;
  res.setHeader("content-type", "application/json; charset=utf-8");
  res.setHeader("cache-control", "no-store");
  res.end(JSON.stringify(body));
}

export default async function apiHandler(req, res) {
  const path = new URL(req.url || "/", "http://localhost").pathname;

  if (path === "/api/health" || path === "/health") {
    return writeJson(res, 200, {
      ok: true,
      service: "naqshkaar-ai-gateway",
      runtime: process.version,
    });
  }

  try {
    const { handler } = await import("../backend/server.js");
    return await handler(req, res);
  } catch (error) {
    console.error("NaqshKaar API bootstrap failure:", error);
    return writeJson(res, 500, {
      error: "AI gateway bootstrap failed.",
      message: String(error?.message || error),
      runtime: process.version,
    });
  }
}
