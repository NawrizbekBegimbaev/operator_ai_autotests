# MVP Scope — UPDATED DRAFT v2.1 (2026-07-24)

> **Draft for review — does NOT replace MVP_SCOPE.md yet.**
> **v2.1: Adham's decisions (2026-07-24) incorporated** — attempt policy, 20s timer, pool model, 2nd-number removal, approved new tasks. Companion docs: `SAVOLLAR_VA_QARORLAR_2026-07-24.md` (client/dev questions + decisions) and the updated `SCOPE_DECISIONS.md`.
>
> **How to read the tables:**
> - **Done** — built, build/tests green per work logs.
> - 🆕 **Open → Done** — was open in the old scope doc, the team has since built it (work-log reference in Notes).
> - ➕ — a row that didn't exist in the old scope doc at all.
> - ❓ — waiting on a client or dev answer (numbered in SAVOLLAR_VA_QARORLAR).
>
> **Reality check on "Done":** code is ready, but live end-to-end calling is still blocked by external steps — OnlinePBX extension enable, Gemini key rotation + billing cap, backend deploy (see bottom).

## 1. Auth & Roles

| Feature | Scope | BE | FE | Notes |
| --- | --- | --- | --- | --- |
| Unified login (3 roles, role-based routing) | MVP | Done | Done | |
| Operator password change | MVP | 🆕 Open → Done | 🆕 Open → Done | WL1 2.1 |
| ROP password change | MVP | 🆕 Open → Done | 🆕 Open → Done | WL1 2.1 |
| Logout + token expiry & refresh | MVP | Done | Done | WL1 2.2: silent refresh instead of alert+logout |
| Account deactivation (ROP→operator, Admin→ROP) | MVP | 🆕 Open → Done | 🆕 Open → Done | WL1 2.3 |
| Operator online/offline presence | MVP | 🆕 Open → Done | 🆕 Open → Done | WL1 2.4 (30s heartbeat, live dot) |
| Single active session per operator | Post-MVP | Open | Open | Two-tab behavior: low priority, warning banner may suffice |

## 2. Admin (Super-admin)

| Feature | Scope | BE | FE | Notes |
| --- | --- | --- | --- | --- |
| ROPs table + CRUD | MVP | Done | Done | WL1 6.1 |
| Single ROP page | MVP | Incomplete | 🆕 Incomplete → Done | WL1 3.4 |
| AmoCRM connection per ROP | MVP | Done | Done | WL2 1.1 (409 fix, secrets preserved) |
| OnlinePBX connection per ROP | MVP | Done | Done | WL1 4.2 (+ API key & webhook token) |
| Operators table under ROP (view) | MVP | Done | 🆕 Incomplete → Done | WL1 3.3 |
| Basic Admin dashboard | Post-MVP | Open | Open | |

## 3. ROP — Rules & settings

| Feature | Scope | BE | FE | Notes |
| --- | --- | --- | --- | --- |
| Pipeline selection (from AmoCRM) | MVP | Done | Done | WL2 1.2: attach auto-syncs leads |
| Statuses synced with AmoCRM | MVP | Done (decided) | Superseded | **Decision 2026-07-24:** dev architecture accepted — statuses auto-mirror from AmoCRM per pipeline; no ROP CRUD. Status names Uzbek-only for MVP |
| Status behavior rules | MVP | 🆕 Open → Done (hardcoded) | n/a | Delivered as the hardcoded queue engine (WL3 §1) |
| Form fields synced with AmoCRM | MVP | Done (decided) | Superseded | **Decision 2026-07-24:** auto-built from the AmoCRM "Operator AI" field group — ROP builds nothing |
| Required / optional fields | MVP | Done | Done | Conditional logic hardcoded |
| Hints for statuses & fields | MVP | Done | Done | |
| ➕ "Mezonlar" settings page (work hours, retry 3h, cap 4, pre-arrival 1h, chala delay 1h, default call 09:00, transition 00:00) | MVP | Done | Done | WL3 1.3 · confirmed: described in ClickUp task |
| ➕ Company description for AI context | MVP | Done | Done | WL3 5.4 · confirmed |
| Operator performance criteria | Post-MVP | Open | Open | |

## 4. ROP — Operators management

| Feature | Scope | BE | FE | Notes |
| --- | --- | --- | --- | --- |
| Operator table + CRUD | MVP | Done | Done | WL1 6.2, WL3 7.4 (PBX ext dropdown — maps operator ↔ 3-digit ext ↔ call audios) |
| Single operator page | MVP | Done | Incomplete | |
| Operator call audios | MVP | Done | Done | |
| Single call page | MVP | Done | Done | |
| Operator performance details | Post-MVP | Open | Open | |
| Operator deactivation | MVP | 🆕 Open → Done | 🆕 Open → Done | = §1 row |
| Attach pipeline to operators | MVP | 🆕 Open → Done | 🆕 Open → Done | **Multi-pipeline accepted (2026-07-24)** · ❓ client Q1.2: confirm real need |
| Online/offline in table | MVP | 🆕 Open → Done | 🆕 Open → Done | WL1 2.4 |
| Per-operator stats (calls today etc.) | MVP | Incomplete | Incomplete | Partial: home counters (WL3 7.3), attempts column (WL3 7.8) |
| ➕ Operator shift screen (start/end/pause, weekly) | MVP | Done | Done | WL1 3.1 · **auto-close will CHANGE:** end shift after N minutes without calls instead of fixed 23:59 (new task; N = dev Q2.10) |
| ➕ ROP weekly attendance table | MVP | Done | Done | WL1 3.2 |

## 5. Operator — Lead management

| Feature | Scope | BE | FE | Notes |
| --- | --- | --- | --- | --- |
| Lead table | MVP | Done | 🆕 Incomplete → Done | WL2 1.4 (own-pipeline, closed/archived hidden — confirmed), WL3 7.8 |
| Lead table: search / filter / sort | MVP | Incomplete | Open | No work-log entry — unchanged |
| Lead detail | MVP | Done | Incomplete | |
| Lead calls table (history, transcripts) | MVP | Done | Done | |
| AI analysis results on lead page | MVP | Incomplete | Incomplete | |
| Manual lead edit → AmoCRM | MVP | Done | Open | WL3 4.4 covers the call flow; lead-page edit UI still open |
| Real-time lead & call updates | MVP | Done | Open | Webhook live & confirmed ("hozirda webhook ishlatvomiz") |
| Sync conflict behavior | MVP | Done | Not in FE | ❓ client Q1.3: do AmoCRM staff keep editing manually? Then define who wins + "lead updated" hint |

## 6. Operator — AI-guided calling

| Feature | Scope | BE | FE | Notes |
| --- | --- | --- | --- | --- |
| Queue algorithm (status-based, shared pool) | MVP | 🆕 Open → Done | 🆕 Done | Pool model confirmed · **Attempt policy DECIDED (2026-07-24): 4 total attempts, unused attempts carry over to next days, then auto-Sifatsiz** (= built behavior) · pool details = dev talk Q2.3 |
| Start Calling flow (modal loop) | MVP | 🆕 Open → Done | 🆕 Open → Done | WL1 1.12/1.13 |
| Pre-call guideline modal | MVP | 🆕 Open → Done | 🆕 Open → Done | WL1 1.8, WL3 7.2 |
| ➕ Pre-call "Call reason" block (previous status, attempt x/4, meeting time) | MVP | Done | Done | WL4 §3 |
| Pause calling | MVP | 🆕 Open → Done | 🆕 Open → Done | WL1 1.9/1.14 |
| 10s countdown before auto-continue | MVP | 🆕 Open → Done | 🆕 Open → Done | WL1 1.9 |
| Post-call confirmation modal (AI-filled, editable) | MVP | 🆕 Open → Done | 🆕 Open → Done | WL1 1.11; WL3 2.3/2.6/7.1 |
| Confirmation expiry timer → auto-sync | MVP | 🆕 Open → Done | 🆕 Open → Done | **20s CONFIRMED (2026-07-24)** — easy to change later if needed |
| Sync to AmoCRM → next lead | MVP | 🆕 Open → Done | 🆕 Open → Done | WL3 §4 |
| Outbound calls via OnlinePBX | MVP | 🆕 Open → Done (code) | 🆕 Done | Live blocked on ext enable in client panel |
| Auto no-answer → Ko'tarmadi status | **Superseded (2026-07-24)** | n/a | n/a | **Decision:** status changes ONLY via human/AI confirm — no auto status write on missed calls. Internal attempt counter + 4×→Sifatsiz covers no-answer. Dev to confirm code matches (Q2.2) |
| ➕ 4× no-answer → auto-"Sifatsiz" (retired from queue, pushed to AmoCRM) | MVP | Done | Done | WL4 2.1–2.4 · AI banned from picking Sifatsiz/Yangi · **client already added the status ✓** |
| Lead locking during a call | MVP | 🆕 Open → Done | Done | WL1 1.2, E2E-tested |
| Empty-queue "next call at HH:MM" message | **Removed (2026-07-24)** | To remove | To remove | Built in WL3 1.5; Adham: remove it — dev task Q2.9 |
| Auto second phone number | **Removed (2026-07-24)** | To remove | To remove | The "2nd number" on AmoCRM contacts is the **OnlinePBX number (78 113 71 61)**, not the lead's — only the lead's own number is dialed. Dev task Q2.8 |
| Incoming call collision | MVP? | Open | Not in FE | Decision #6 still pending |
| ➕ Uchrashuv → Bugun keladi auto-transition | MVP | Done | n/a | WL3 1.7 · loop concern resolved (idempotent) |
| ➕ After-hours retry → next working morning | MVP | Done | n/a | WL3 1.8 |
| ➕ Arrival-time change rule (moved to tomorrow+ → back to Uchrashuv flow; still today → restart Bugun-keladi flow) | **Approved (2026-07-24)** | Open | Open | New ClickUp task |
| ➕ Paid / not-paid manual field | **Approved (2026-07-24)** | Open | Open | New ClickUp task; "came but didn't pay" → next-call time set by center staff in AmoCRM |

## 7. AI features

| Feature | Scope | BE | Notes |
| --- | --- | --- | --- |
| Audio transcription (Uz + Ru) | MVP | Done | WL3 5.1–5.4 + WL4 §1 (caps, skip 0-sec calls) · model upgraded — better Uzbek (confirmed) |
| AI extraction vs configured statuses/fields | MVP | Done | Pipeline-scoped; never picks Sifatsiz/Yangi (WL4 2.2/2.3) |
| AI analysis of operator performance | Post-MVP | Open | |
| Typed-value extraction ("dushanba" → date) | MVP | 🆕 Open → Done | WL3 2.5 |

## 8. Integrations

| Feature | Scope | BE | Notes |
| --- | --- | --- | --- |
| AmoCRM: pull (pipelines, statuses, leads, fields) | MVP | Done | Per-pipeline status mirror; deleted/archived leads excluded (confirmed) |
| AmoCRM: webhooks | MVP | Done | Live & confirmed; `AMOCRM_WEBHOOK_URL` env on prod/staging still pending (dev Q2.11) |
| AmoCRM: two-way sync | MVP | Done | WL3 §3–4 |
| ➕ AmoCRM rate-limit protection | MVP | Done | WL3 3.5/3.6 · webhook reduces load but protection stays; watch at multi-ROP scale |
| OnlinePBX: call audio | MVP | Done | |
| OnlinePBX: token-based requests | MVP | Done | WL1 4.1 |
| OnlinePBX: outbound calling | MVP | 🆕 Open → Done (code) | Live pending ext enable |
| ➕ Gemini security: API key in header | MVP | Done | WL4 4.1 — old key **must be rotated** (see below) |
| ➕ Gemini cost guard: billing-cap 429 not retried | MVP | Done | WL4 4.2 |
| AI cost model & usage limits | Post-MVP | Open | |

## 9. Marketing / Landing

| Feature | Scope | Status | Notes |
| --- | --- | --- | --- |
| Public landing page | MVP | Done | v2 design deployed (confirmed) |
| Landing intake form + API | MVP | Done | Leads now visible in admin panel, not Google Sheets (confirmed) |

## 10. Cross-cutting

| Feature | Scope | Status | Notes |
| --- | --- | --- | --- |
| Admin app i18n (UZ/RU) | ➕ Built | Done | WL3 9.1 + WL4 · confirmed (agreed verbally) |
| ➕ Integration health card (last sync, webhook status, stuck calls) | **Approved as new feature (2026-07-24)** | Open | New ClickUp task |

---

## Open questions (full list in SAVOLLAR_VA_QARORLAR_2026-07-24.md)

**Client:** phoneless leads possible? · multi-pipeline needed? · do AmoCRM staff keep editing manually? · out-of-hours requested call times · Bugun-keladi missed confirmation call retry.
**Dev:** auto-Chala rule exists? · no-answer status behavior matches decision? · pool-model details · queue-0 display · slow-AI cap · deploy order · Marketplace OAuth · 2nd-number removal · empty-queue message removal · inactivity shift close (N minutes?) · `AMOCRM_WEBHOOK_URL` set?
**TBD:** attempt-counter reset on human status edits.

## External steps blocking "really done" (not code)

1. 🚨 **Rotate the Gemini API key** — the old one leaked into logs (WL4).
2. **Raise/remove the Gemini spending cap** — transcription currently dies on billing 429.
3. **Deploy `back`** to staging/prod → then `admin`/`landing`.
4. **`AMOCRM_WEBHOOK_URL`** on prod/staging + staging origin in `HTTP_CORS_ORIGINS`.
5. **Enable the operator extension** in the OnlinePBX panel.
6. ~~"Sifatsiz" status in every AmoCRM pipeline~~ — **done, client added it ✓**
