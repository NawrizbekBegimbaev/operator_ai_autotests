# MVP Scope Document

## 1. Auth & Roles

| Feature | Scope | BE Status | FE Status |
| --- | --- | --- | --- |
| Unified login page for
Super-admin / ROP /
Operator with role-based
routing | In MVP | Done | Done |
| Operator password change | In MVP | Open | Open |
| ROP password change | In MVP | Open | Open |
| Logout + session/token expiry & refresh (1d refresh token) | In MVP | Done | Done |
| Account deactivation (ROP deactivates operator, Admin deactivates ROP) | In MVP | Open | Open |
| Operator online/offline presence tracking | In MVP | Open | Open |
| Single active session per operator (Multiple tabs) | Post-MVP | Open | Open |

## 2. Admin (Super-admin)

| Feature | Scope | BE Status | FE Status |
| --- | --- | --- | --- |
| ROPs table + Create / Edit /
Delete ROP | In MVP | Done | Done |
| Single ROP | In MVP | Incomplete | Incomplete |
| AmoCRM connection per
ROP (CRUD) | In MVP | Done | Done |
| OnlinePBX connection per
ROP (CRUD) | In MVP | Done | Done |
| Operators table under ROP
(view only) | In MVP | Done | Incomplete |
| Basic Admin dashboard | Post-MVP | Open | Open |

## 3. ROP — Rules (pipeline & criteria configuration)

| Feature | Scope | BE Status | FE Status |
| --- | --- | --- | --- |
| Pipeline selection (pull pipelines from AmoCRM) | In MVP | Done | Done |
| Status types CRUD, synced with AmoCRM statuses | In MVP | Done | Incomplete |
| Status behavior rules | In MVP | Open | Not in FE |
| Form fields CRUD, synced with AmoCRM fields | In MVP | Done | Incomplete |
| Required and optional fields | In MVP | Done | Done |
| Hint for status & form fields (to help AI understand) | In MVP | Done | Done |
| Operator (operator performance
criteria) | Post-MVP | Open | Open |

## 4. ROP — Operators management

| Feature | Scope | BE Status | FE Status |
| --- | --- | --- | --- |
| Operator table + Create / Edit / Delete | In MVP | Done | Done |
| Single operator page | In MVP | Done | Incomplete |
| Operator call audios (list, playback)
 | In MVP | Done | Done |
| Single call page  | In MVP | Done | Done |
| Operator performance details | Post-MVP | Open | Open |
| Operator deactivation (keep data, kill access) | In MVP | Open | Open |
| Attach pipeline to operators | In MVP | Open | Open |
| Operator online/offline status in the table | In MVP | Open | Open |
| Other data (like how many leads he called today) belongs to that operator | In MVP | Open | Open |

## 5. Operator — Lead management

| Feature | Scope | BE Status | FE Status |
| --- | --- | --- | --- |
| Lead table  | In MVP | Done | Incomplete |
| Lead table: search, filter by status, sort by next-call time | In MVP | Incomplete | Open |
| Lead detail | In MVP | Done | Incomplete |
| Lead calls table (call history per lead, transcripts) | In MVP | Done | Done |
| AI analysis results displayed
on lead page | In MVP | Incomplete | Incomplete |
| Manual edit of lead status & form fields → syncs to AmoCRM | In MVP | Done | Open |
| Real-time lead & call updates | In MVP | Done | Open |
| Sync conflict behavior (AmoCRM edited the same lead) | In MVP | Done | Not in FE |

## 6. Operator — AI-guided calling system

| Feature | Scope | BE Status | FE Status |
| --- | --- | --- | --- |
| The queue algorithm — which lead comes next? | In MVP | Open | Not in FE |
| Start Calling flow | In MVP | Open | Open |
| Pre-call guideline modal (target status, form fields, overview) | In MVP | Open | Open |
| Pause calling | In MVP | Open | Open |
| Action countdown timer
(10s, 10-9-8…) before auto-continue | In MVP | Open | Open |
| Post-call confirmation modal (AI-extracted status/fields/overview,
editable) | In MVP | Open | Open |
| Confirmation expiry timer → auto-sync | In MVP | Open | Open |
| Sync to AmoCRM → loop to next lead | In MVP | Open | Open |
| Placing/receiving calls on a lead via OnlinePBX | In MVP | Open | Not in FE |
| Auto-detect no-answer from OnlinePBX and mark Ko'tarmadi | In MVP | Open | Not in FE |
| Lead locking during a call (Two operators on the same pipeline) | In MVP | Open | not in FE |
| Empty-queue state | In MVP | Open | Open |
| Incoming call collision | In MVP | Open | Not in FE |

## 7. AI features

| Feature | Scope | BE status |
| --- | --- | --- |
| Audio transcription (Language support: Uzbek + Russian) | In MVP | Done |
| AI extracts against ROP-configured statuses/fields (+hint) | In MVP | Done |
| AI analysis for operator performance | Post-MVP | Open |
|  Typed-value extraction ("dushanba" → date, relative to call date, Asia/Tashkent) | In MVP | Open |

## 8. Integrations

| Feature | Scope | BE Status |
| --- | --- | --- |
| AmoCRM: pipelines, statuses, leads, custom fields (pull) | In MVP | Done |
| AmoCRM: lead updates via webhook (push→us) | In MVP | Done |
| AmoCRM: two-way sync (status, fields, overview, sent_to_amocrm flag) | In MVP | Done |
| OnlinePBX: call audio retrieval | In MVP | Done |
| OnlinePBX: operator token based requests
 | In MVP | Done |
| OnlinePBX: outbound calling from lead | In MVP | Open |
| AI cost model & usage limits | Post-MVP | Open |

## 9. Marketing / Landing

| Feature | Scope | Status |
| --- | --- | --- |
| Public landing page | In MVP | Done |
| Landing intake form + API | In MVP | Done |