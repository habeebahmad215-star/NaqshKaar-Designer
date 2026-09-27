import { createServer } from "node:http";
import handler from "../backend/server.js";

export default async function api(req, res) {
  return handler(req, res);
}
