# OperatorAI — Ish jurnali v4 (uchinchi jurnaldan keyin)

**Muddat:** 22–24 Iyul 2026 (davomi)
**Repolar:** `admin` (React), `back` (Go), `landing` (Vite)
**Holat:** build / test / lint — hammasi yashil (BE `go build ./...` + `go test ./...`, FE `bun run build`)

**Jami:** 14 task · Backend/DB: 9 · Frontend/UI: 3 · Infra/CI: 1 · Tahlil/diagnostika: 1 · Bug tuzatildi: 8 (shundan 1 tasi — o'zimiz kiritgan regressiya) · Xavfsizlik: 1

Bu jurnal — `WORK_LOG_3.md` (44 task, Queue Engine + i18n) dan **keyingi** ishlar. Asosiy mavzular: **stagingni o'ldirgan transkripsiya "storm" regressiyasini tuzatish** (o'zimiz kiritgan bug), **AI'ning "Sifatsiz"ni noto'g'ri tanlashi + 4× ko'tarmaslik biznes qoidasi**, **qo'ng'iroq oldidan status-aware "Qo'ng'iroq sababi" bloki (Task 4)**, va **Gemini xavfsizligi/xarajati** (API kaliti leak + billing-cap retry isrofi).

Teglar: **BE** = Backend · **FE** = Frontend · **UI** = interfeys · **DB** = ma'lumotlar bazasi · **AI** = Gemini/prompt · **OPS** = DevOps · **SEC** = xavfsizlik · **CI** = build/deploy

---

## 1 · Staging o'lik edi (502) — transkripsiya "storm" regressiyasi — 4 task

**Bu — o'zimiz kiritgan bug.** Oldingi sessiyada transkripsiyaga "self-healing retry" (qayta urinish) qo'shdik, lekin uchta chegara qo'ymadik: (a) o'lik hodisani qayta-qayta urinardi, (b) parallel transkripsiyalar soni cheklanmagan, (c) har xato `os.Stderr`ga to'kilardi. Natijada retry sweep + webhook bursti → cheksiz gorutina + xotira → **konteyner OOM restart loop** → staging 502. Dozzle loglari (`TRANSCRIBE_ERR` toshqini + "Container stopped") sababni tasdiqladi.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 1.1 | **Urinish chegarasi (attempt cap)** | BE, DB | `onlinepbx_webhook_events`ga `transcription_attempts INT NOT NULL DEFAULT 0` (migratsiya `20260723102607_transcription_attempts`). `ListPendingTranscriptionEvents` endi `transcription_attempts < $2` (maks **5**) filtrlaydi — doimo yiqiladigan hodisa 5 urinishdan keyin tashlab yuboriladi. `BumpTranscriptionAttempts(id, permanent, cap)` — xatoda hisoblagichni oshiradi; **permanent** xato (yo'q audio 404 / `ErrAudioUnavailable` / `ErrAudioNotFound`) darrov cap'ga sakraydi. |
| 1.2 | **Parallellik chegarasi (semaphore)** | BE | `maxConcurrentTranscriptions = 3` — har transkripsiya audio yuklab, Gemini chaqiradi; cheksiz fan-out aynan OOM yo'li edi. `transcribeSem chan struct{}` bilan bir vaqtda faqat 3 tasi ishlaydi, qolgani navbatda kutadi. |
| 1.3 | **"Tahlil qilinadigan" gate** | BE | `ListPendingTranscriptionEvents` endi `operator_id IS NOT NULL AND coalesce(dialog_duration_sec,0) > 0` ham talab qiladi. Operatorsiz yoki 0 soniyalik (javob berilmagan) qo'ng'iroqlar umuman transkripsiya qilinmaydi — bekorga Gemini chaqiruvi yo'q. |
| 1.4 | **Log toshqinini to'xtatish** | BE, OPS | `os.Stderr`ga to'g'ridan-to'g'ri yozish olib tashlandi (`"os"` import ham). O'rniga `SetTranscriptionErrorLogger` callback → tarkibiy `logger.Warn()`. Xato loglari endi cheklangan va tuzilgan (JSON), stderr'ni bosib ketmaydi. |

**Natija:** foydalanuvchi Dozzle orqali staging tiklanganini tasdiqladi (deploydan keyin). Storm bog'langan barcha interfeys/repo/test stublari yangi imzolarga moslashtirildi (`BumpTranscriptionAttempts`, `notifyingRepository`, 4 ta test stub).

---

## 2 · AI "Sifatsiz" muammosi + 4× ko'tarmaslik qoidasi — 4 task

Foydalanuvchi haqiqiy suhbat transkriptini ko'rsatdi — AI uni noto'g'ri "Sifatsiz" deb belgilagan edi. Ikki qismli ish: (a) AI hech qachon noto'g'ri "Sifatsiz"/"Yangi" tanlamasin, (b) lekin **4 marta qo'ng'iroq ko'tarilmasa** — lid avtomatik "Sifatsiz"ga tushsin va boshqa terilmasin.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 2.1 | **`StatusClassSifatsiz` klass** | BE | Status klass enum'iga `Sifatsiz` qo'shildi (`String()` → `"sifatsiz"`, `classify` → nom `"sifatsiz"` bo'lsa). **`queueRank`ga qo'shilmadi** — Sifatsiz lidlar hech qachon qo'ng'iroq navbatiga tushmaydi. |
| 2.2 | **"Sifatsiz"/"Yangi"ni tanlovdan chiqarish** | BE | `isOperatorSelectableStatus` + `isSelectableStatus` endi type=1, amo_id 142/143 dan tashqari **nomida "sifatsiz" yoki "yangi"** bor statuslarni ham rad etadi. AI ham, operator dropdowni ham bularni qo'ng'iroq natijasi sifatida ko'rsatmaydi. |
| 2.3 | **Extraction prompt kuchaytirildi** | BE, AI | Extraction promptiga aniq natija→status xaritasi: uchrashuv kelishildi → "uchrashuv/bugun keladi"; qayta qo'ng'iroq → "keyingi qo'ng'iroq"; qaror yo'q → "chala"; **haqiqiy suhbatda hech qachon yangi-lid yoki Sifatsiz emas**. |
| 2.4 | **4× ko'tarmaslik → avto-Sifatsiz** | BE, DB | `ListNoAnswerExhaustedLeads` (ko'tarmadi statusidagi, `attempts_count >= max` lidlar) + `ExhaustedLead` contract. `runNoAnswerExhaustionForROP` — o'z statuslari/principalini oladi, tugagan "ko'tarmadi" lidlarni pipeline'ning "Sifatsiz"iga o'tkazadi (AmoCRM'ga push bilan). `RunAppointmentTransitions` ichida **mustaqil** chaqiriladi (uchrashuv logikasi early-return qilsa ham ishlashi uchun alohida). Idempotent: ko'chirilgach lid endi ko'tarmadi statusida emas. Test: `TestRunTransitionsMovesExhaustedNoAnswerLeadToSifatsiz`. |

---

## 3 · Task 4 — Qo'ng'iroq oldidan "Qo'ng'iroq sababi" bloki — 3 task

To'rt asosiy queue taskidan oxirgisi. Operator qo'ng'iroq qilishdan **oldin** ko'radigan guideline oynasiga status-aware "nega bu lidga qo'ng'iroq qilyapmiz" konteksti qo'shildi.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 3.1 | **`previous_status_id` ustuni** | BE, DB | `amocrm_leads`ga `previous_status_id UUID NULL` (FK `amocrm_pipeline_statuses`, `ON DELETE SET NULL`; migratsiya `20260723114957_lead_previous_status`). Upsert status **o'zgarganda** eskisini saqlaydi (`CASE WHEN status_id IS DISTINCT FROM EXCLUDED.status_id ...`). Bu "Ko'tarmadi" lid uchun asosiy kontekst: u "Uchrashuv vaqti"dan tushganmi (uchrashuvni tasdiqlash) yoki "Markazga keldi"dan (to'lovni undirish). Entity + mapper ham yangilandi. |
| 3.2 | **`CallReason` + `buildCallReason`** | BE | `Guideline`ga `Reason CallReason` maydoni. `buildCallReason` — **best-effort** (hech qachon guideline'ni yiqitmaydi): joriy + oldingi status nomi/klassi (pipeline statuslardan), urinish soni x/maks (`lead_call_states` + settings), oxirgi/keyingi qo'ng'iroq vaqti, kelish/uchrashuv vaqti, 2-raqam, majburiy field yorliqlari. `IsFirstCall` — hali terilmagan lid uchun "birinchi bog'lanish". HTTP DTO `callReasonResponse` + `fillCallReason` (vaqtlar RFC3339). |
| 3.3 | **Frontend "Qo'ng'iroq sababi" bloki** | FE, UI, i18n | Yangi `calling-call-reason.tsx` — status klassiga qarab sarlavha (yangi/ko'tarmadi/chala/uchrashuv/bugun keladi/keyingi qo'ng'iroq/markazga keldi/default) + tafsilot qatorlari (urinish, oldingi bosqich, uchrashuv/kelish vaqti, oxirgi urinish, 2-raqam). Amber ton — oxirgi urinish + bugun keladi; ko'k — qolgani. Faqat ro'yxatdan o'tgan Iconify to'plami ishlatildi. Kokpit qorong'i-mavzu oroliga mos. UZ + RU kalitlar (`calling.reason.*`). |

---

## 4 · Gemini xavfsizlik va xarajat — 2 task

Staging loglarida ikkita jiddiy narsa ko'rindi: Gemini billing-cap 429 (barcha transkripsiya yiqilardi) va — muhimi — **API kaliti loglarga ochiq chiqib ketardi**.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 4.1 | **API kaliti leak — barcha 5 chaqiruv sayti** | SEC, BE | Kalit URL query'da edi (`...:generateContent?key=AIza...`). Transport xatosi (timeout/DNS) `Do()`dan qaytganda Go'ning `*url.Error` to'liq URL'ni — kalit bilan — log'ga bosardi. Kalit **`?key=` URL'dan `x-goog-api-key` header'ga** ko'chirildi. Barcha 5 sayt: transkripsiya, forma extraction (`onlinepbx/service.go`), operator guidance (`operator_guidance.go`), deal analysis ×2 (`amocrm/deal_analysis.go`). `grep generateContent?key=` → bo'sh. |
| 4.2 | **Billing-cap 429 → permanent (retry isrofi)** | BE | `isGeminiSpendingCapExceeded` — xatoda `"spending cap"` yoki `"exceeded its monthly"` bo'lsa **permanent** deb belgilaydi (attempt darrov cap'ga). Retry befoyda — billing oshgunicha 429 qoladi. Oddiy daqiqalik rate-limit 429 (o'zi tuzaladigan) esa hamon retry bo'ladi — faqat billing xabari match qilinadi, umumiy `RESOURCE_EXHAUSTED` emas. |

---

## 5 · i18n davomi va CI — 1 task

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 5.1 | **Frontend CI — bun lockfile** | CI, FE | i18n bog'liqliklari `npm` bilan qo'shilgan edi (`package-lock.json`) — lekin admin **bun** ishlatadi (`bun install --frozen-lockfile`), CI shu tufayli yiqildi. `bun install` bilan `bun.lock` qayta yaratildi, `package-lock.json` o'chirildi + `.gitignore`ga qo'shildi. `bun install --frozen-lockfile` → "no changes" bilan tasdiqlandi. |

---

## 6 · Tahlil — asl 4 taskning bajarilish darajasi (diagnostika)

Foydalanuvchi asl 4 ta queue-engine spetsifikatsiyasini yubordi va "qaysilari qanchalik tayyor" deb so'radi. Kod bilan solishtirildi:

- **Task 1 (statusga qarab navbat):** ✅ Bajarilgan. Spetsifikatsiyadagi *"lidlar operatorga biriktiriladi"* qismi **noto'g'ri** edi — foydalanuvchi ham buni to'g'ri belgiladi. Haqiqiy/to'g'ri xatti-harakat: **umumiy hovuz** — qaysi operator bo'sh bo'lsa, navbatdagi keyingi lidni oladi (lid affinity yo'q). Kod aynan shuni bajaradi.
- **Task 2 (AmoCRM'ga bir marta yuborish):** ✅ Funksional bajarilgan — status-klass idempotentligi orqali (ko'chirilgach lid endi o'sha klassda emas). Alohida `sent_to_amocrm` flagi shart emas.
- **Task 3 (uchrashuv/bugun keladi o'tishlari):** ✅ Bajarilgan (`RunAppointmentTransitions`, WL3).
- **Task 4 (qo'ng'iroq sababi bloki):** shu sessiyada bajarildi (bo'lim 3).

---

## Diagnostika va topilgan asosiy sabablar

- **Stagingni o'zimiz o'ldirdik** — oldingi sessiyada qo'shgan transkripsiya retry'i uchta chegarasiz edi (o'lik hodisa cheksiz retry + parallellik cheki yo'q + stderr toshqini) → OOM restart loop → 502. Bu WL4'ning eng katta darsi: "self-healing" retry doimo attempt-cap + concurrency-cap + tuzilgan log bilan birga bo'lishi kerak.
- **Gemini API kaliti loglarda ochiq edi** — transport xatosi URL'ni bosib chiqaradi; `?key=` bo'lgani uchun sirt ochilgan. Header'ga o'tkazish yagona ishonchli yechim.
- **429 ikki xil bo'ladi** — daqiqalik rate-limit (retry foydali) va oylik billing-cap (retry befoyda). Ikkalasi ham `RESOURCE_EXHAUSTED`, lekin faqat billing xabari bo'yicha ajratish kerak.
- **AI "Sifatsiz"ni noto'g'ri tanlagan** — status filtri + prompt mustahkamligi bilan tuzatildi; "Sifatsiz" endi faqat **biznes qoidasi** (4× ko'tarmaslik) yoki qo'lda qo'yiladi, AI suhbatdan emas.

## Tashqi qadamlar (foydalanuvchi tomonida)

- **⚠️ Gemini kalitini ROTATE qilish** — `AIzaSy...FflLw` allaqachon loglarda ochilgan (kompromis). AI Studio'da eskisini o'chir, yangi yarat, `.env`/docker-compose'dagi `GEMINI_API_KEY`ni yangila. Kod fixi faqat **kelajakdagi** leak'ni to'xtatadi.
- **Gemini billing-cap** — [ai.studio/billing](https://ai.studio/billing) spending cap oshir/o'chir, aks holda transkripsiya umuman ishlamaydi.
- **Backend deploy** — staging/prodga `back` deploy qilinsin (storm fixi 502'ni tuzatadi + Sifatsiz + Task 4 + gemini fixlari). Migratsiyalar deploy'da avto-qo'llanadi.
- **`AMOCRM_WEBHOOK_URL`** prod/staging `.env`ga (real-time), staging `HTTP_CORS_ORIGINS`ga staging admin origin.

## Standing qoida

`back`/`admin` repolari **push qilinmaydi** — foydalanuvchi lokalda tekshirib keyin o'zi push qiladi. Shu sessiyada barcha ish lokalda build/test yashil holatda qoldirildi; migratsiyalar lokal DB'ga qo'llandi (`make migrate-apply`).
