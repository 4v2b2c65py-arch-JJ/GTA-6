const fs = require('fs');
const path = require('path');

const BASELINE_PATHS = [
  path.join(process.cwd(), 'build', 'web', 'data', 'env', 'environment.json'),
  path.join(process.cwd(), 'build', 'web', 'environment.json'),
  path.join(process.cwd(), 'data', 'env', 'environment.json'),
];
const STATE_PATHS = [
  path.join(process.cwd(), 'build', 'web', 'data', 'env', 'state.json'),
  path.join(process.cwd(), 'data', 'env', 'state.json'),
  '/tmp/spatial-avy-env-state.json',
];

function readJSON(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; }
}
function ensureDir(p) { try { fs.mkdirSync(path.dirname(p), { recursive: true }); } catch {} }
function writeFirst(paths, obj) {
  let wrote = null;
  for (const p of paths) {
    try {
      ensureDir(p);
      fs.writeFileSync(p, JSON.stringify(obj, null, 2) + '\n', 'utf8');
      wrote = p; break;
    } catch {}
  }
  return wrote;
}
function deepMerge(a, b) {
  if (Array.isArray(b)) return b;
  if (b && typeof b === 'object') {
    const out = { ...(a && typeof a === 'object' && !Array.isArray(a) ? a : {}) };
    for (const k of Object.keys(b)) out[k] = deepMerge(out[k], b[k]);
    return out;
  }
  return b === undefined ? a : b;
}
function collectBaseline() {
  let base = null;
  for (const p of BASELINE_PATHS) { const j = readJSON(p); if (j) { base = j; base._baseline_path = p; break; } }
  return base || { schema: 'spatial-avy.env.v1', environment: { paths: {} } };
}
function collectState() {
  for (const p of STATE_PATHS) { const j = readJSON(p); if (j) { j._state_path = p; return j; } }
  return {};
}
function detectRuntime(req) {
  const h = req.headers || {};
  return {
    api: '/api/env',
    method: req.method,
    host: h['x-forwarded-host'] || h.host || null,
    proto: h['x-forwarded-proto'] || null,
    vercel_env: process.env.VERCEL_ENV || null,
    vercel_region: process.env.VERCEL_REGION || null,
    vercel_url: process.env.VERCEL_URL || null,
    deployment_url: process.env.VERCEL_URL ? ('https://' + process.env.VERCEL_URL) : null,
    node: process.version,
    platform: process.platform,
    arch: process.arch,
    cwd: process.cwd(),
    timestamp: new Date().toISOString(),
  };
}
async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  return await new Promise((resolve) => {
    let data = '';
    req.on('data', c => { data += c; if (data.length > 2e6) req.destroy(); });
    req.on('end', () => { try { resolve(data ? JSON.parse(data) : {}); } catch { resolve({ raw: data }); } });
    req.on('error', () => resolve({}));
  });
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'OPTIONS') return res.status(204).end();

  const baseline = collectBaseline();
  const saved = collectState();
  let payload = {};
  if (req.method === 'POST') payload = await readBody(req);

  const runtime = detectRuntime(req);
  const client = payload.client || payload.runtime_client || {};
  const merged = deepMerge(deepMerge(baseline, saved), {
    schema: 'spatial-avy.env.v1',
    updated_at: new Date().toISOString(),
    api: { name: 'env', ok: true, endpoint: '/api/env' },
    environment: {
      runtime: runtime,
      client: client,
      paths: deepMerge((baseline.environment && baseline.environment.paths) || {}, (payload.paths || {})),
      data_paths: deepMerge((baseline.environment && baseline.environment.data_paths) || {}, (payload.data_paths || {})),
    },
    state: deepMerge(saved.state || {}, payload.state || {}),
  });
  if (payload.fill) merged.filled = deepMerge(merged.filled || {}, payload.fill);

  let saved_to = null;
  if (req.method === 'POST' || req.query.save === '1') saved_to = writeFirst(STATE_PATHS, merged);

  return res.status(200).json({
    ok: true,
    api: 'env',
    saved_to,
    env: merged,
  });
};
