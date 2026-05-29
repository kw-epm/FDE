import { useEffect, useState } from "react";
import {
  getHealth,
  getDemoTickets,
  getTicket,
  getCustomers,
  resolveStream,
  type Health,
  type DemoTicket,
  type Customer,
  type Disposition,
  type AgentStep,
  type ResolveRequest,
} from "./api";

const TIER_CLASS: Record<number, string> = { 1: "tier1", 2: "tier2", 3: "tier3" };

function tierLabel(d: Disposition): string {
  if (d.action === "DEFER_PHONE") return "DEFER";
  return `TIER ${d.tier}`;
}

const FLAG_HIGH = ["LEGAL", "ABUSIVE", "ENTERPRISE_CONTRACT"];
const FLAG_MID = ["ENTITLEMENT", "IDENTITY_VERIFICATION", "DISTRESS"];

// the `draft` field is a customer reply, a holding message, or an INTERNAL briefing — label by who produced it
function draftLabel(d: Disposition): string {
  if (d.handled_by === "escalation") return "internal briefing — for the human specialist (not sent to the customer)";
  if (d.handled_by === "entitlement") return "customer holding message";
  if (d.handled_by === "resolution") return "customer reply";
  return "draft";
}

// turn http(s) URLs into clickable links (odd split indices are the captured URL)
function linkify(text: string, keyBase: string) {
  return text.split(/(https?:\/\/[^\s<>()]+)/g).map((seg, i) =>
    i % 2 === 1 ? (
      <a key={`${keyBase}-${i}`} href={seg} target="_blank" rel="noopener noreferrer">{seg}</a>
    ) : (
      seg
    ),
  );
}

// render **bold** + clickable links in the draft (newlines/list numbers already show via pre-wrap)
function renderDraft(text: string) {
  return text.split(/\*\*(.+?)\*\*/g).map((part, i) =>
    i % 2 === 1 ? (
      <strong key={i}>{linkify(part, `b${i}`)}</strong>
    ) : (
      <span key={i}>{linkify(part, `t${i}`)}</span>
    ),
  );
}

function flagClass(f: string): string {
  if (FLAG_HIGH.includes(f)) return "high";
  if (FLAG_MID.includes(f)) return "mid";
  return "low";
}

// the flags are shown as chips, so strip the raw ['X','Y'] / (flags=[...]) list from the sentence
function cleanRationale(s: string): string {
  return s
    .replace(/\(?flags=\[[^\]]*\]\)?/g, "")
    .replace(/\[[^\]]*\]/g, "")
    .replace(/\s{2,}/g, " ")
    .replace(/\s+([;.,])/g, "$1")
    .replace(/\(\s*\)/g, "")
    .trim();
}

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [demos, setDemos] = useState<DemoTicket[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [result, setResult] = useState<Disposition | null>(null);
  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [channel, setChannel] = useState("chat");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [loadedId, setLoadedId] = useState<string | null>(null);
  const [attempted, setAttempted] = useState(false);

  useEffect(() => {
    getHealth().then(setHealth).catch((e) => setError(String(e)));
    getDemoTickets().then(setDemos).catch((e) => setError(String(e)));
    getCustomers().then(setCustomers).catch((e) => setError(String(e)));
  }, []);

  const channelIsPhone = channel === "phone";
  const customerMissing = !customerId;
  const subjectMissing = !channelIsPhone && !subject.trim(); // phone has no typed subject/body
  const bodyMissing = !channelIsPhone && !body.trim();
  const formInvalid = customerMissing || subjectMissing || bodyMissing;
  // only flag fields after they try to resolve, not on load
  const showCustomerError = customerMissing && attempted;
  const showSubjectError = subjectMissing && attempted;
  const showBodyError = bodyMissing && attempted;

  async function loadDemo(t: DemoTicket) {
    setError(null);
    setResult(null);
    setSteps([]);
    try {
      const d = await getTicket(t.id);
      setChannel(d.channel);
      setSubject(d.subject);
      setBody(d.body);
      setCustomerId(d.customer_id);
      setLoadedId(d.ticket_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  function clearForm() {
    setChannel("chat");
    setSubject("");
    setBody("");
    setCustomerId("");
    setLoadedId(null);
    setResult(null);
    setSteps([]);
    setError(null);
    setAttempted(false);
  }

  async function run(req: ResolveRequest) {
    setLoading(true);
    setError(null);
    setResult(null); // clear the previous result while the agents run
    setSteps([]);
    await resolveStream(
      req,
      (s) => setSteps((prev) => [...prev, s]),
      (d) => {
        setResult(d);
        setLoading(false);
      },
      (e) => {
        setError(e);
        setLoading(false);
      },
    );
  }

  return (
    <div className="app">
      <header>
        <h1>ResolveOne <span className="sub">CloudServe multi-channel customer resolution</span></h1>
        {health && (
          <div className={`provider ${health.live ? "live" : "mock"}`}>
            provider: <strong>{health.provider}</strong>
            {health.live
              ? " — agentic (Haiku + Sonnet)"
              : " — offline mock (architecture only; set ANTHROPIC_API_KEY for the agentic path)"}
            <span className="corpus"> · {health.customers.toLocaleString()} customers · {health.kb_articles} KB articles</span>
            {health.agents && (
              <div className="topology">
                topology: <strong>coordinator</strong> → {health.agents.filter((a) => a !== "coordinator").join(" · ")}
              </div>
            )}
          </div>
        )}
      </header>

      <div className="grid">
        <section className="panel">
          <h2>Demo paths</h2>
          <p className="hint">Click a path to load it into the form, then press Resolve. Edit any field first to improvise.</p>
          <ul className="demos">
            {demos.map((t) => (
              <li key={t.id}>
                <button disabled={loading} onClick={() => loadDemo(t)}>
                  <span className="tid">{t.id}</span>
                  <span className="tlabel">{t.label}</span>
                </button>
              </li>
            ))}
          </ul>
          <button className="clear" disabled={loading} onClick={clearForm}>✕ Clear form</button>

          <h2>Ticket {loadedId && <span className="loaded">loaded {loadedId}</span>}</h2>
          <label>
            Channel
            <select value={channel} onChange={(e) => setChannel(e.target.value)}>
              <option value="chat">chat</option>
              <option value="email">email</option>
              <option value="phone">phone</option>
            </select>
          </label>
          <label>
            Customer
            <select
              className={showCustomerError ? "invalid" : ""}
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
            >
              <option value="">— select a customer —</option>
              {customers.map((c) => (
                <option key={c.customer_id} value={c.customer_id}>
                  {c.name} · {c.plan_tier} · {c.customer_id}
                </option>
              ))}
            </select>
            {showCustomerError && <span className="field-err">pick a customer to resolve</span>}
          </label>
          <label>
            Subject
            <input
              className={showSubjectError ? "invalid" : ""}
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="weird charge on my card"
            />
            {showSubjectError && <span className="field-err">please fill this field</span>}
          </label>
          <label>
            Message
            <textarea
              className={showBodyError ? "invalid" : ""}
              rows={5}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="There's a charge on my card I want my money back for."
            />
            {showBodyError && <span className="field-err">please fill this field</span>}
          </label>
          <button
            className="primary"
            disabled={loading}
            onClick={() => {
              if (formInvalid) {
                setAttempted(true);
                return;
              }
              run({ channel, subject, body, customer_id: customerId });
            }}
          >
            Resolve
          </button>
        </section>

        <section className="panel result">
          <h2>Agent run</h2>
          {error && <p className="error">{error}</p>}
          {steps.length === 0 && !result && !error && (
            <p className="hint">Pick a demo path or paste a ticket — you'll see each agent run live.</p>
          )}
          {steps.length > 0 && (
            <div className="trace">
              {steps.map((s, i) => {
                // amber appears ONLY as the live spinner; finished steps are green, everything else gray
                const active = loading && i === steps.length - 1 && s.phase === "calling";
                const icon = active ? "spin" : s.phase === "done" ? "ok" : "info";
                return (
                  <div key={i} className={`tstep ${s.phase}`}>
                    <span className={`ticon ${icon}`} />
                    <span className="tagent">{s.agent}</span>
                    {s.model
                      ? <span className="tmodel ai">AI · {s.model}</span>
                      : <span className="tmodel det">deterministic</span>}
                    <span className="tlabel">
                      {s.label}
                      {s.detail ? ` — ${s.detail}` : ""}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
          {result && (
            <>
              <div className="verdict">
                <span className={`badge ${TIER_CLASS[result.tier] || "defer"}`}>{tierLabel(result)}</span>
                <span className="action">{result.action}</span>
                {result.route_to && <span className="route">→ {result.route_to}</span>}
              </div>

              <table className="meta">
                <tbody>
                  <tr><th>handled by</th><td><span className="agent">{result.handled_by ?? "—"}</span></td></tr>
                  <tr><th>ticket</th><td>{result.ticket_id} ({result.channel})</td></tr>
                  <tr><th>issue_type</th><td>{result.issue_type ?? "—"} <span className="dim">conf {result.confidence}</span></td></tr>
                  <tr><th>kb cited</th><td>{result.kb_articles.length ? result.kb_articles.join(", ") : "—"}</td></tr>
                  <tr><th>guardrails</th><td>
                    {result.guardrail_flags.length
                      ? result.guardrail_flags.map((f) => (
                          <span key={f} className={`flag ${flagClass(f)}`}>{f}</span>
                        ))
                      : "—"}
                  </td></tr>
                  <tr><th>LLM calls</th><td>{result.llm_calls_this_request}{result.llm_calls_this_request === 0 && result.action === "DEFER_PHONE" ? " (phone never transcribed)" : ""}</td></tr>
                  <tr><th>customer</th><td>{result.customer_record_found ? "record found" : "NOT found (fail-loud)"}</td></tr>
                </tbody>
              </table>

              <div className="rationale"><strong>why:</strong> {cleanRationale(result.rationale)}</div>

              {result.draft && (
                <div className={`draft ${result.handled_by === "escalation" ? "internal" : ""}`}>
                  <div className="draft-h">{draftLabel(result)}</div>
                  <pre>{renderDraft(result.draft)}</pre>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}
