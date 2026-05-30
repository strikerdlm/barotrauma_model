/**
 * Typed fetch client for the ``api/`` FastAPI sidecar. Wraps
 * ``GET /api/scenarios``, ``GET /api/scenarios/{key}``, and
 * ``POST /api/simulate``. No physics — the Python engine stays
 * authoritative.
 *
 * The dev server proxies ``/api/*`` to ``http://localhost:8000`` via
 * ``vite.config.ts``. In production set ``VITE_API_BASE`` to override.
 */

import type {
  ProfilePresetInfo,
  ProfilePresetKey,
  SimulateRequest,
  SimulateResponse,
} from '../types/v2';

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') ??
  '';

export class ApiError extends Error {
  readonly status: number;
  readonly detail?: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  let res: Response;
  try {
    res = await fetch(url, init);
  } catch (err) {
    throw new ApiError(
      `Network error calling ${path}: ${(err as Error).message}. ` +
        `Is the Python API running on :8000? (uvicorn api.main:app --reload --port 8000)`,
      0,
    );
  }
  if (!res.ok) {
    let detail: unknown;
    try {
      detail = await res.json();
    } catch {
      detail = await res.text();
    }
    // A 404 whose body is exactly Starlette's default {"detail":"Not Found"}
    // means the route is missing — i.e. a *different* FastAPI app is answering
    // on :8000, not this one. (A real backend 404, e.g. an unknown preset key,
    // carries a descriptive detail and must not get this hint.)
    const routeMissing =
      res.status === 404 &&
      typeof detail === 'object' &&
      detail !== null &&
      (detail as { detail?: unknown }).detail === 'Not Found';
    const hint = routeMissing
      ? ' — is the barotrauma API the process on :8000? Verify with ' +
        '`curl localhost:8000/api/health` (expect "version":"2.2.1"); ' +
        'a different server may be answering on that port.'
      : '';
    throw new ApiError(
      `API ${res.status} at ${path}: ${JSON.stringify(detail)}${hint}`,
      res.status,
      detail,
    );
  }
  return (await res.json()) as T;
}

export function health(): Promise<{ status: string; version: string }> {
  return request('/api/health');
}

export function listScenarios(): Promise<ProfilePresetInfo[]> {
  return request('/api/scenarios');
}

export function getScenario(key: ProfilePresetKey): Promise<ProfilePresetInfo> {
  return request(`/api/scenarios/${key}`);
}

export function simulate(req: SimulateRequest): Promise<SimulateResponse> {
  return request('/api/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
}

/**
 * Convenience helper: simulate with a preset + default patient. The
 * backend fills defaults for every unset field.
 */
export function simulatePreset(
  preset: ProfilePresetKey,
  patient: SimulateRequest['patient'] = {},
  options: SimulateRequest['options'] = {},
): Promise<SimulateResponse> {
  return simulate({
    patient,
    profile: { preset },
    options,
  });
}
