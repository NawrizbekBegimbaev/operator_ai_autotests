# OperatorAI — Ish jurnali (task-ma-task)

**Muddat:** 8–9 Iyul 2026
**Repolar:** `admin` (React), `back` (Go)
**Holat:** build / test / lint — hammasi yashil

**Jami:** 36 task · Frontend/UI: 19 · Backend/DB: 21 · HIGH bug tuzatildi: 3

Teglar: **BE** = Backend · **FE** = Frontend · **UI** = interfeys · **DB** = ma'lumotlar bazasi · **OPS** = DevOps

---

## 1 · AI qo'ng'iroq tizimi (asosiy feature) — 15 task

Operatorning avtomatik qo'ng'iroq oqimi: navbatdan lid → tayyorgarlik → qo'ng'iroq → AI tahlil → tasdiqlash → keyingi lid. Mahsulotning yadrosi — noldan qurildi.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 1.1 | Ma'lumotlar bazasi sxemasi | DB, BE | 3 yangi jadval: `operator_pipelines`, `lead_call_states`, `call_sessions` + Atlas migratsiya. Qo'ng'iroq holati AmoCRM mirroridan alohida saqlanadi. |
| 1.2 | Atomik navbat va lid qulflash | BE, DB | Keyingi lidni `FOR UPDATE SKIP LOCKED` bilan atomik tanlash — ikki operator bir lidni hech qachon olmaydi. Qisqa muddatli lock (lease). |
| 1.3 | Navbat logikasi (usecase) | BE | `NextLead` — lid + guideline to'plami (lead + status + maydonlar + guidance); `QueueCount` — lid claim qilmasdan navbat soni. |
| 1.4 | Qo'ng'iroq sessiyasi holat-mashinasi | BE | Dial → poll (call↔event correlation) → confirm (AmoCRM push + keyingi qo'ng'iroq rejalash + unlock) → skip (reschedule). To'liq FSM. |
| 1.5 | Operator ↔ pipeline biriktirish (API) | BE | ROP operatorlarni pipeline'larga biriktiradi; operator faqat o'ziga biriktirilgan pipeline lidlariga qo'ng'iroq qiladi. CRUD + ruxsat. |
| 1.6 | HTTP routelar | BE | `/v1/calling/*` (queue, next, dial, session, confirm, skip) + `/v1/operator-pipelines`. Huma OpenAPI, Bearer himoya. |
| 1.7 | **UI — "Navbat sozlash" ekrani (ROP)** | UI, FE | Har operator uchun karta; pipeline'lar chip sifatida — bosib biriktirish/olib tashlash. AmoCRM sinxronlanmagan bo'lsa ogohlantirish. |
| 1.8 | **UI — Guideline (tayyorgarlik) paneli** | UI | Gradientli sarlavha + lead ismi/telefoni, joriy status chip, narx; maqsad-statuslar chiplari; to'ldiriladigan maydonlar checklist (majburiy belgi + hint); ROP guidance matni. |
| 1.9 | **UI — 10s countdown ring** | UI | Aylanma taymer (10→0) avtomatik dial'gacha; darrov qo'ng'iroq yoki pauza; 3 soniyada qizil holat. |
| 1.10 | **UI — Dialing holati** | UI | Pulslanuvchi telefon ikonasi, lead ma'lumoti, "Qo'ng'iroq / AI tahlil" spinneri, o'tkazish tugmasi. |
| 1.11 | **UI — Tasdiqlash (confirmation) paneli** | UI | AI xulosasi karta; status select (AI tanlagani default); har maydon tahrirlanadi (majburiy bo'sh — qizil); keyingi qo'ng'iroq vaqti datetime picker. |
| 1.12 | **UI — Modal-driven loop** | UI | Butun oqim to'liq-sahifadan popup modal'ga: stepper (Tayyorgarlik → Qo'ng'iroq → Tasdiqlash), tasdiqdan keyin avtomatik keyingi lid. |
| 1.13 | **UI — Launcher hero ekran** | UI, BE | Navbat soni katta + "Qo'ng'iroqni boshlash" tugmasi modal ochadi; bo'sh navbat holati. Yangi `/calling/queue` endpoint. |
| 1.14 | Tasdiqlash auto-sync taymeri | UI, BE | Confirmation modalda 20s countdown — operator harakatsiz qolsa AI tavsiyasi avto AmoCRM'ga sync + keyingi lid. Tahrir taymerni reset qiladi; pauza bor. (TOR talabi) |
| 1.15 | Backend testlar + E2E | BE | Usecase testlar + jonli DB E2E: biriktirish → navbat → guideline → skip → reschedule; lock/lease DB'da tekshirildi. |

---

## 2 · Auth va foydalanuvchi hisoblari — 4 task

Kirish, sessiya va hisob boshqaruvi — MVP'ning ochiq bo'lgan asosiy qismlari.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 2.1 | Parolni o'zgartirish (o'zi) | UI, BE | Account menyuda dialog (eski/yangi/tasdiq) + `/auth/change-password`. Eski parol tekshiriladi. E2E. |
| 2.2 | Token refresh oqimi (FE) | UI, BE | Ilgari token tugasa `alert` + logout. Endi 401'da jim `/auth/refresh` + retry (single-flight), `withCredentials`, backend CORS credentials. E2E. |
| 2.3 | Hisobni faolsizlantirish | UI, BE | Login + Refresh inactive'ni bloklaydi. ROP operatorni, superadmin ROP'ni o'chiradi (ma'lumot saqlanadi, kirish kesiladi). Jadvalda toggle. |
| 2.4 | Online/offline holat (presence) | UI, BE, DB | `operator_presence` jadval + heartbeat/presence endpoint. Operator har 30s heartbeat; ROP jadvalida avatarda yashil/kulrang nuqta (jonli). |

---

## 3 · Operator boshqaruvi va UI — 5 task

Operatorlar ekranlari va navigatsiya tuzatildi; ish-vaqti kuzatuvi.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 3.1 | **UI — Ish vaqti ekrani (operator)** | UI | Smena boshlash/tugatish + tanaffus toggle, jonli soat, holat chip, shu haftalik jadval. |
| 3.2 | **UI — Davomat ekrani (ROP)** | UI | Barcha operatorlarning haftalik davomat jadvali (vaqtlar, ishlangan/tanaffus, tanaffuslar soni), hafta navigatsiyasi. |
| 3.3 | **UI — Navigatsiya tuzatildi** | UI | Superadmin'dan flat "Operatorlar" olib tashlandi — operatorlar ROP ichida drill-down orqali (operator ROP'ga tegishli). |
| 3.4 | **UI — ROP operatorlar sahifasi qayta tuzildi** | UI | "Orqaga" yuqoriga; takroriy sarlavha olib tashlandi; jadval header'siz embed; ROP kartasidan operator-maydonlar (PBX, oylik, rol) olib tashlandi. |
| 3.5 | **UI — Qayta ishlatiladigan jadval komponenti** | UI | Users jadvaliga `embedded` rejimi — boshqa sahifa ichida header/wrapper'siz. Kod takrorlanmaydi. |

---

## 4 · Integratsiyalar — 3 task

OnlinePBX va AmoCRM ulanish qatlamlari — hujjatlar va real akkauntlar bilan solishtirildi.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 4.1 | OnlinePBX client qayta yozildi | BE | Eski kod 7 xil auth variantini taxmin qilardi (noto'g'ri). Demo'dan aniq spec: `auth.json` → `x-pbx-authentication` → `call/now.json`, muvaffaqiyat `status=="1"`, session cache + re-auth. Testlar bilan. |
| 4.2 | **UI — OnlinePBX ulash formasi** | UI | Ilgari faqat domain. Endi API key + webhook token maydonlari — ROP real qo'ng'iroq uchun panel kalitini kirita oladi. |
| 4.3 | AmoCRM webhook himoyasi | BE | Webhook autentifikatsiyasiz edi (soxta so'rov → lid o'chirish xavfi). Endi `AMOCRM_WEBHOOK_TOKEN` talab qilinadi (constant-time compare). |

---

## 5 · Infratuzilma va DevOps — 3 task

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 5.1 | Lokal muhit | OPS | `config.yml`, `.env`, docker-compose (Postgres 55432, DB `operatorai`), HTTP 8090. Portlar boshqa docker loyihalari bilan to'qnashmaydi. |
| 5.2 | CORS — lokal + prod fix | BE | Lokal: har localhost origin ruxsat. Prod: `*` + credentials xatosi (login buzilgan) — endi request origin reflect qilinadi. |
| 5.3 | Makefile + boot log | OPS | `make run` Go yo'li tuzatildi (Linux snap → PATH); boot'da server porti + docs URL log'da. |

---

## 6 · Bug va UI tuzatishlar — 4 task

Foydalanuvchi topgan xatolar va FE/BE nomuvofiqliklari.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 6.1 | ROP yaratishda username konflikti | UI | Har ROP bir xil qattiq-kodlangan username yuborardi (2-chisi 409). Formaga username maydoni qo'shildi; eski TS resolver xatosi ham yo'q bo'ldi. |
| 6.2 | Operator yaratishda 422 xato | UI | Backend `pbx_extension` talab qilardi, formada yo'q edi. PBX extension maydoni qo'shildi. |
| 6.3 | rop = company / company_id tuzatildi | UI, BE | ROP operatorlari `company_id` null qaytargani uchun ko'rinmasdi. Endi `rop.id` + `role='operator'` filtri (ROP o'zi ro'yxatga tushmaydi). |
| 6.4 | Lint tuzatish | BE | `golangci-lint` errcheck (`tx.Rollback`) — kodbaza uslubiga moslab tuzatildi. 0 issue. |

---

## 7 · Tahlil va sifat — 2 task

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 7.1 | Kodbaza + hujjatlar tahlili | Tahlil | admin + back o'rganildi; TOR v0.2, AmoCRM, OnlinePBX referenslari solishtirildi; "to'g'ri yo'ldamizmi?" bahosi + yetishmagan MVP qismlar. |
| 7.2 | Sifat auditi + 3 HIGH bug fix | BE | Audit. Tuzatildi: (1) goroutine `recover()` — panic jarayonni o'ldirmaydi; (2) DB tranzaksiya — forma yangilashda ma'lumot yo'qolmaydi; (3) AmoCRM webhook auth. |

---

## Keyingi bosqich — integratsiya kalitlari kutilmoqda

Kod tayyor, ammo to'liq sinov uchun tashqi hisob ma'lumotlari kerak:

- **OnlinePBX** — real domain + panel API key → operator qo'ng'irog'ini jonli sinash.
- **Gemini** — AI API key → yozuv transkripsiyasi + maydon/status ajratish.
- **AmoCRM** — OAuth/token → lidlar sinxronlashi, keyin butun oqim real ma'lumot bilan.

Kod bo'yicha qolgan MVP qismlar: sana ajratish ("dushanba"→sana, Asia/Tashkent), avto "Ko'tarmadi" (javob bermadi), sinxronlash konflikti, lidlar AmoCRM-kanban ko'rinishi.
