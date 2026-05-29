export interface Health {
  provider: string;
  customers: number;
  kb_articles: number;
  live: boolean;
  topology?: string;
  agents?: string[];
}

export interface DemoTicket {
  id: string;
  channel: string;
  label: string;
}

export interface Disposition {
  ticket_id: string;
  tier: number;
  issue_type: string | null;
  confidence: number;
  kb_articles: string[];
  action: string;
  route_to: string | null;
  draft: string | null;
  guardrail_flags: string[];
  rationale: string;
  model_used: string | null;
  handled_by: string | null;
  channel: string;
  customer_id: string;
  subject: string;
  llm_calls_this_request: number;
  customer_record_found: boolean;
}

export interface ResolveRequest {
  ticket_id?: string;
  channel?: string;
  subject?: string;
  body?: string;
  customer_id?: string;
}

// API lives under the app base (e.g. "/2905/") so it works behind the nginx /2905/ path
const API = `${import.meta.env.BASE_URL}api`;

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error((detail as { detail?: string }).detail || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const getHealth = () => fetch(`${API}/health`).then((r) => json<Health>(r));

export const getDemoTickets = () =>
  fetch(`${API}/tickets`).then((r) => json<{ demo: DemoTicket[] }>(r)).then((d) => d.demo);

export interface TicketDetail {
  ticket_id: string;
  channel: string;
  subject: string;
  body: string;
  customer_id: string;
}

export const getTicket = (id: string) =>
  fetch(`${API}/tickets/${encodeURIComponent(id)}`).then((r) => json<TicketDetail>(r));

export interface Customer {
  customer_id: string;
  name: string;
  plan_tier: string;
}

export const getCustomers = () =>
  fetch(`${API}/customers`).then((r) => json<{ customers: Customer[] }>(r)).then((d) => d.customers);

export const resolve = (req: ResolveRequest) =>
  fetch(`${API}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  }).then((r) => json<Disposition>(r));

export interface AgentStep {
  type: "step";
  agent: string;
  phase: "calling" | "done" | "info";
  model?: string | null;
  label: string;
  detail?: string;
}

// Streams Server-Sent Events from /api/resolve/stream: one step per agent call as it
// happens, then the final disposition. Lets the UI show live per-agent progress.
export async function resolveStream(
  req: ResolveRequest,
  onStep: (s: AgentStep) => void,
  onResult: (d: Disposition) => void,
  onError: (msg: string) => void,
): Promise<void> {
  const res = await fetch(`${API}/resolve/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok || !res.body) {
    let detail = `HTTP ${res.status}`;
    try {
      detail = ((await res.json()) as { detail?: string }).detail ?? detail;
    } catch {
      /* non-JSON body */
    }
    onError(detail);
    return;
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = buf.indexOf("\n\n")) >= 0) {
      const raw = buf.slice(0, idx).trim();
      buf = buf.slice(idx + 2);
      if (!raw.startsWith("data:")) continue;
      const ev = JSON.parse(raw.slice(5).trim());
      if (ev.type === "step") onStep(ev as AgentStep);
      else if (ev.type === "result") onResult(ev.disposition as Disposition);
      else if (ev.type === "error") onError(ev.detail as string);
    }
  }
}
