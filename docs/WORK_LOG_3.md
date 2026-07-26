# OperatorAI — Ish jurnali v3 (ikkinchi jurnaldan keyin)

**Muddat:** 17–22 Iyul 2026 (davomi)
**Repolar:** `admin` (React), `back` (Go), `landing` (Vite)
**Holat:** build / test / lint — hammasi yashil (BE go test + vet, FE vite build)

**Jami:** 44 task · Backend/DB: 24 · Frontend/UI: 14 · Infra/Landing: 3 · Tahlil/diagnostika: 3 · i18n: 1 (katta) · Bug tuzatildi: 18

Bu jurnal — `WORK_LOG_2.md` (12 task, AmoCRM ulash) dan **keyingi** ishlar. Asosiy mavzular: **statusga asoslangan avtomatik qo'ng'iroq navbati (Queue Engine)**, dinamik forma AI bilan avto-to'ldirish, AmoCRM sinxron ishonchliligi (bir necha kritik bug), transkripsiya ishonchliligi, va **butun adminka rus tiliga (i18n)**. Bir necha bug 15-iyuldan beri jim ishlamay turgan edi — shu sessiyada topilib tuzatildi.

Teglar: **BE** = Backend · **FE** = Frontend · **UI** = interfeys · **DB** = ma'lumotlar bazasi · **AI** = Gemini/prompt · **OPS** = DevOps · **i18n** = tarjima

---

## 1 · Qo'ng'iroq navbati dvijoki (Queue Engine) — 8 task

Sessiyaning eng katta ishi. Operatorga lid biriktirilmaydi — hamma operator bitta umumiy hovuzdan navbat bo'yicha qo'ng'iroq qiladi. Navbat AmoCRM statusiga qarab avtomatik tuziladi.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 1.1 | **Status klass tizimi** (`classifyStatusName`) | BE | Har AmoCRM statusi klassga bo'linadi: Yangi lid, Ko'tarmadi, Chala, Keyingi qo'ng'iroq vaqti, Uchrashuv/Bugun keladi. Nom kichik harf + apostrof tozalab, substring bo'yicha aniqlanadi; noma'lum status → Other → navbatga umuman tushmaydi. |
| 1.2 | **Qat'iy navbat tartibi** (`queueRank`) | BE | Bugun keladi → Keyingi qo'ng'iroq vaqti → Chala → Ko'tarmadi → Yangi lid. Bo'sh operator har doim eng yuqori ustuvorlikdagi due lidni oladi (`ClaimNextLeadForOperator` — atomik claim + lock). |
| 1.3 | **Mezonlar (ROP-sozlanadigan vaqt parametrlari)** | BE, FE, DB | Yangi `rop_call_settings` jadvali + Mezonlar sahifasi: ish boshi/oxiri (08:00/20:00), retry interval (180 daq), umrbod urinish cheki (4), uchrashuvdan oldin (60 daq), chala kechikish (60 daq), standart call vaqti (09:00), Bugun-keladi transition (00:00). Bo'sh maydon = standart qiymat. `EffectiveCallSettings` + validatsiya. |
| 1.4 | **Umrbod 4-urinish "Ko'tarmadi" cheki** | BE, DB | Lid 4 marta ko'tarmasa umrbod navbatdan chiqadi (`RecordLeadCallAttempt` lifetime hisoblagich). Faqat qo'lda status o'zgarganda reset (`ResetLeadAttemptsOnStatusChange` — upsert paytida har yozuv yo'lida ishlaydi). |
| 1.5 | **Bo'sh navbat holati** (keyingi due vaqt) | BE, FE | Navbat bo'sh bo'lsa "keyingi qo'ng'iroq HH:MM da" ko'rsatiladi (`GetNextUpcomingDueForOperator` — bugungi kelajak due). Operator qachon qaytishni biladi, bo'sh ekranga qaramaydi. |
| 1.6 | **Avto ikkinchi telefon** | BE, FE | 1-raqam ko'tarmasa AmoCRM kontaktining 2-raqamiga avto o'tadi (`fetchLeadContactPhones` barcha telefonlarni oladi; FE `phoneIndexRef`). |
| 1.7 | **Uchrashuv kuni → Bugun keladi avto-transition** | BE, OPS | Har 5 daqiqada scheduler: uchrashuv/kelish sanasi bugun bo'lgan lidlar avtomatik "Bugun keladi" statusiga o'tadi (`RunAppointmentTransitions`). |
| 1.8 | **Retry ish vaqtidan tashqari — ertaga ertalabga** | BE | Ish soatidan keyingi retry keyingi ish kuni ertalabga suriladi (tunda operator qo'ng'iroq qilmaydi). |

---

## 2 · Dinamik forma + AI to'ldirish oqimi — 6 task

Forma qo'lda qurilmaydi — AmoCRM "Operator AI" field guruhidan avto-quriladi. AI call davomida/keyin fieldlarni to'ldiradi, operator tasdiqlaydi.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 2.1 | **AmoCRM guruhidan avto forma qurish** | BE, AI | `SyncFormFromAmoCRMOperatorGroup` — nomida "operator" bo'lgan field guruhini topib dinamik forma + fieldlar + dinamik statuslar yaratadi. ROP hech narsa qurmaydi. Har sync sweep'da yangilanadi. |
| 2.2 | **Guruhning to'liq nusxasini tanlash** | BE | Bir guruh har pipeline uchun alohida nusxada saqlanadi; forma eng ko'p fieldli nusxaga bog'lanadi (5 vs 8 field muammosi — "Markazga kelish vaqti" ko'rinmay yurgan edi). |
| 2.3 | **Jonli forma call davomida (2 ustunli grid)** | FE, UI | Confirm oynasi mockup bo'yicha 2 ustunli grid; operator call vaqtida ham fieldlarni to'ldiradi, uning qiymati AI'nikidan ustun. |
| 2.4 | **AI select variantlarini promptga berish** | BE, AI | Extraction prompt select fieldlarga `allowed_values` ro'yxatini beradi va "aynan ro'yxatdan ko'chir" deb buyuradi — paraphrase qilingan qiymat confirm'da tashlanmaydi. |
| 2.5 | **AI nisbiy sanani hal qilish** | BE, AI | Prompt "bugun/ertaga/dushanba" → aniq YYYY-MM-DD (call sanasiga nisbatan, Asia/Tashkent). Navbat due vaqti uchun kerak. |
| 2.6 | **Confirm timing: hammasi birdan** | FE, UI | Submission ikki bosqichda keladi (bo'sh standart → AI qiymatlari + xulosa). Ilgari FE `submission.id` borligini tekshirib sanoqni erta boshlardi. Endi `ai_summary` kelguncha "AI tahlil qilmoqda…" banneri turadi, sanoq boshlanmaydi; AI tugagach hamma field birdan to'ladi. |

---

## 3 · AmoCRM sinxron ishonchliligi — 7 task

Bir necha kritik bug 15-iyuldan beri jim ishlamay turgandi (sync yarim-singan). Shu sessiyada topildi.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 3.1 | **`contact_phones` NOT NULL bug (sync muzlagan)** | BE, DB | Kontaktsiz lidda nil massiv SQL NULL sifatida yozilib, `null value in column "contact_phones" violates not-null constraint` bilan **butun sweep birinchi kontaktsiz lidda to'xtardi** — 16-iyuldan keyingi lidlar umuman kelmagan. Fix: nil → bo'sh massiv (`nonNilStrings`). |
| 3.2 | **Jim yutilgan sync xatolari** | BE | `_ = s.leadSync(...)` — sync yiqilsa log jim edi. `SetSyncErrorLogger` callback qo'shildi, endi har muvaffaqiyatsiz sweep `warn` bilan logga tushadi. |
| 3.3 | **O'chirilgan lidlarni tozalash (prune)** | BE, DB | AmoCRM list API o'chirilgan lidni shunchaki qaytarmaydi — bizda prune yo'q edi, o'lik lidlar navbatda qolardi. `MarkAmoCRMLeadsDeletedExcept` — to'liq muvaffaqiyatli sweep'dan keyin qaytmagan lidlar `is_deleted`. Xatoda mass-delete bo'lmaydi. |
| 3.4 | **Webhook avto-registratsiya** | BE, OPS | `AMOCRM_WEBHOOK_URL` o'rnatilsa backend har ulangan AmoCRM akkauntiga webhook'ni **o'zi ro'yxatdan o'tkazadi** (`EnsureWebhookSubscription` — add/update/status/delete lead). Qo'lda AmoCRM sozlash shart emas. ROP boshiga bir marta (dedup). |
| 3.5 | **Rate-limit + 429 retry** | BE | Webhook bursti + 2-daqiqalik sweep birga AmoCRM ~7 req/s limitini portlatib **429 Too Many Requests** berardi (lidlar yo'qolardi). `waitAmoRequestSlot` (200ms oraliq) + 429'da 2s/4s retry. |
| 3.6 | **Sweep tejamkorligi (freshness marks)** | BE, DB | O'zgarmagan lidlar (remote `updated_at` siljimagan) qayta tortilmaydi (`ListAmoCRMLeadSyncMarks`). 147 lid × 2 so'rov o'rniga odatda 1-2 so'rov — rate-limit yengillashdi. |
| 3.7 | **Webhook ingest yengillashtirish** | BE | Har webhook hodisasida to'liq pipeline-sync qilinmaydi (statuslarni scheduler baribir yangilaydi) — faqat kelgan lidning o'zi tortiladi. |

---

## 4 · Confirm → AmoCRM push to'g'riligi — 6 task

Operator tasdiqlaganda ma'lumot AmoCRM'ga to'g'ri lidga tushishi kerak edi — bir necha bug.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 4.1 | **Claimed lidga yozish (yangi lid emas)** | BE | Ilgari push telefon bo'yicha yangi "Dynamic form submission" lid yaratardi (pipeline'da hech kim tanimaydigan). Endi operator qo'ng'iroq qilgan **o'sha lidga** yoziladi: status + fieldlar + nota bir PATCH'da (`updateLeadForCall`), keyin lokal ko'zgu darrov yangilanadi. |
| 4.2 | **Select field enum resolution** | BE | Filliallar = "1364009" (enum ID) matn sifatida ketardi → 400 "noto'g'ri tanlov". Endi select fieldlar `{"enum_id": N}` bilan yoziladi (`resolveSelectEnumID` — display matn yoki enum ID → to'g'ri enum; mos kelmasa tashlanadi). |
| 4.3 | **Status faqat lead pipeline'idan** | BE | AI boshqa pipeline statusini ("18:00") tanlab, push lidni boshqa pipeline'ga surardi → 400. `resolveAmoCRMStatusForPipeline` — status faqat lidning o'z pipeline'idan olinadi, pipeline hech qachon o'zgarmaydi. |
| 4.4 | **Manual confirm field-push** | BE | Manual confirm (AI submission yo'q) faqat statusni push qilardi — operator yozgan fieldlar lokalda qolardi. Endi `PushManualLeadUpdate` — fieldlar ham claimed lidga ketadi. |
| 4.5 | **Operator avto-tanlash** | BE | "Operator" select fieldi sessiya operatorining ismi yoki ichki raqami bo'yicha avto-tanlanadi (`autoFillOperatorSelect`). AI paraphrase qilgan qiymat haqiqiy variant bilan almashtiriladi. |
| 4.6 | **AI status extraction pipeline-scoping** | BE, AI | AI'ga 89 ta butun-ROP dynamic status berilardi (chalkash nomlar), begonasini tanlardi → deal "ko'tarmadi"da qolardi. Endi AI faqat **shu lead pipeline'ining** statuslarini ko'radi (`filterDynamicStatusesToPipeline`) + lead telefon orqali topiladi (`resolveEventLead` — `onlinepbx_event_id` bog'i autofill'da NULL edi). Prompt: real suhbatda "ko'tarmadi" tanlamaydi. |

---

## 5 · Transkripsiya ishonchliligi va sifati — 4 task

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 5.1 | **JSON parse bug (transkripsiya muzlagan)** | BE, AI | Gemini uzun transkriptni bo'laklarga bo'lib, obyektdan keyin ortiqcha `]` token qo'shardi; eski "birinchi `{` → oxirgi `}`" parser buni ushlolmasdi → `json.Unmarshal`: `invalid character ']' after top-level value`. Xato yutilar, oyna abadiy "AI tahlil qilmoqda…"da qotardi. Fix: qavs-balanslovchi parser (satr ichidagi `}`ni hisobga oladi). |
| 5.2 | **Self-healing retry sweep** | BE, OPS | Transkripsiya faqat yangi eventda ishlardi — bir marta yiqilsa abadiy qotardi. Endi har 30 soniyada transkriptsiz qolgan oxirgi qo'ng'iroqlarni topib qayta urinadi (`RetryPendingTranscriptions`). |
| 5.3 | **Gemini model yangilash (flash)** | BE, AI | Transkripsiya eng arzon/zaif `gemini-2.5-flash-lite` bilan edi — o'zbekcha nomlarni (Bodomzor, Buxoro) yaxshi eshitmasdi. `GEMINI_TRANSCRIPT_MODEL` → `gemini-2.5-flash` (sezilarli aniqroq STT). |
| 5.4 | **Kompaniya tavsifi (AI kontekst)** | BE, FE, DB | ROP `company_description` yozadi (nima sotadi, filiallar, atamalar); har AI promptga qo'shiladi (transkripsiya nomlarni to'g'ri taniydi, tahlil kontekstda). Yangi ustun + Mezonlar sahifasida kart + `GET/PUT /v1/users/{id}/company-description`. |

---

## 6 · Status ko'zgusi arxitekturasi — 3 task

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 6.1 | **Dynamic status kaliti (nom → amocrm_status_id)** | BE, DB | `dynamic_form_statuses` nom bo'yicha ROP-wide kalitlangandi — ROP'da 17 pipeline hammasida "ko'tarmadi"/"bugun keladi" bor, nom bir xil bo'lgani uchun faqat bittasi qolardi. Migratsiya: kalit `(rop_id, amocrm_status_id)`ga — har pipeline statusi o'z ko'zgusiga ega. Dedup + FK repoint bilan. |
| 6.2 | **Eski status/field/guruh prune (FK unlink)** | BE, DB | AmoCRM'da status/field o'chirilib-qayta yaratilsa eski ID push'da 400 berardi. Prune query'lar dynamic forma bog'ini uzib, o'lik qatorlarni o'chiradi; auto-sync keyingi aylanishda jonli guruhga qayta bog'laydi. `DeleteAmoCRMPipelineStatusesExcept` + custom-field/guruh prune guruh bo'ylab. |
| 6.3 | **System statuslarni tanlovdan chiqarish** | BE | Неразобранное (type=1), Успешно/Закрыто (142/143) — qo'ng'iroq natijasi bo'la olmaydi. `isOperatorSelectableStatus`/`isSelectableStatus` — AI ham, operator dropdown ham bularni ko'rsatmaydi. |

---

## 7 · UI/UX tuzatishlar — 10 task

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 7.1 | **Confirm oyna kompakt + 2 ustun** | FE, UI | Fieldlar 2 ustunli grid (mockup bo'yicha), size kichraytirildi (ostidagi fieldlar scroll qilmasdan ko'rinadi), `maxWidth: 760`. |
| 7.2 | **Guideline chiplar (kompakt)** | FE, UI | Pre-call guideline field chip klasteri — professional dizayn, ixcham. |
| 7.3 | **Bosh sahifa "0 qo'ng'iroq" bug** | BE | "Qo'ng'iroqlar" ro'yxati (bosh sahifa hisoblagichi ham) tanlangan-pipeline filtridan lidsiz qo'ng'iroqlarni yashirardi — 850+ hodisa yo'qolgandek. Filtr endi faqat **boshqa pipeline bitimli** qo'ng'iroqlarni yashiradi. |
| 7.4 | **User management: CRM→Ichki raqam** | FE, UI, BE | CRM ustuni (dead field) olib tashlandi, o'rniga Ichki raqam (ext) dropdown. Operator create'da OnlinePBX ext ro'yxatdan tanlanadi. |
| 7.5 | **Company ID → Kompaniya nomi (editable)** | FE, BE, DB | Edit'dagi Company ID → Kompaniya nomi (ROP uchun editable); operator company nomi ROP'dan olinadi (`COALESCE rop.company_name`). |
| 7.6 | **Nav subheader non-collapsible** | FE, UI | Navigatsiya bo'lim sarlavhalari yig'ilmaydigan qilindi. |
| 7.7 | **Sidebar user card → account drawer** | FE, UI | Chap pastdagi user card bosilsa account drawer ochiladi (hamma rol: superadmin/ROP/operator). |
| 7.8 | **Deals jadvali: Status/Urinishlar** | FE | NARX/YUBORILGAN ustunlari (dead/kam qiymatli) → Status (StatusPill) / Urinishlar; oxirgi call vaqti. |
| 7.9 | **Smena avto-yopish (23:59)** | BE, OPS | Yopilmasdan qolgan smenalar kun oxirida (`work_day + 1kun - 1sek` Asia/Tashkent) avto-yopiladi (`CloseStaleShifts`, 30 daq scheduler). |
| 7.10 | **Cheksiz polling + Verto race fix** | FE | Birinchi-call Verto registratsiya race (avto-dial effect); Chrome "Outdated Optimize Dep" 504 (`optimizeDeps.entries` + kesh tozalash). |

---

## 8 · Landing va route — 3 task

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 8.1 | **Yangi landing → main (push)** | Infra, OPS | `new_landing` eski `landing` o'rniga; Dockerfile (bun→node:22 npm ci), GitLab CI, `.env`/`.env.prod`. Push qilindi (f97af89). |
| 8.2 | **`.dockerignore` `.env.local` fix** | Infra | Vite `.env.local`ni `.env`dan ustun qo'yadi — developer localhost URL'i prod image'ga tushib **har landing lidini yo'qqa yuborardi**. `.dockerignore`ga `*.local` qo'shildi (9b939b3). Bundle grep bilan tasdiqlangan. |
| 8.3 | **Route rename `/v1/leads`** | BE, FE, Infra | Chalkash `/v1/google-sheets/leads` → `/v1/leads` (eski alias `Deprecated`, ishlashda davom etadi). Lidlar Google Sheets emas, o'z DB'ga (superadmin Lidlar sahifasi); Sheets ixtiyoriy ko'zgu. Sheets sozlanmaganda lid saqlanmasligi bug'i ham tuzatildi (store-first). Admin + landing yangi manzilga. |

---

## 9 · Rus tili (i18n) — 1 katta task

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 9.1 | **Butun adminka ikki tilda (UZ/RU)** | FE, i18n | `i18next` + `react-i18next` o'rnatildi; config (o'zbekcha standart, ruscha variant, localStorage'da saqlanadi). Header'da UZ/RU almashtirgich (login sahifasida ham). **541 tarjima kaliti, 10 namespace** (common/nav/calling/calls/home/work/users/leads/amocrm/auth), uz↔ru to'liq parity. Barcha ekran: navigatsiya, kokpit, confirm, calls, foydalanuvchi boshqaruvi, davomat, lidlar, tariflar, login (brend paneli + Zod validatsiya). Sana/vaqt til bo'yicha lokalizatsiya. AI/data allaqachon ikki tilda (prompt gaplashilgan tilni saqlaydi) — o'zgartirilmadi. |

---

## Diagnostika va topilgan asosiy sabablar

Bu sessiyada ko'p vaqt "nega ishlamayapti" ni aniqlashga ketdi. Eng muhim topilmalar:

- **Sync 15-iyuldan beri yarim-singan edi** — `contact_phones` NOT NULL xatosi butun sweep'ni birinchi kontaktsiz lidda to'xtatgan; xato yutilgani uchun ko'rinmagan (task 3.1, 3.2).
- **Transkripsiya JSON parse'da jim yiqilardi** — `invalid character ']'`; oyna abadiy "tahlil qilmoqda"da qotardi (task 5.1).
- **Status doim "ko'tarmadi"da qolardi** — ikki sabab: (a) AI begona pipeline statusini tanlardi (lead topilmagani uchun filtr no-op — task 4.6); (b) mirror nom-kolliziyasi tufayli to'liq emas edi (task 6.1). "Ko'tarmadi"ni ba'zan **haqiqiy AmoCRM xodimi** qo'ygan (events log tasdiqladi) — biz emas.
- **429 rate-limit** — webhook bursti lidlarni yo'qotardi (task 3.5, 3.6).

## Tashqi qadamlar (kod tayyor)

- **Prod deploy tartibi:** avval `back` (route rename + sync fixlar + webhook), keyin `admin`/`landing`. Landing yangi `/v1/leads`ga o'tsa-yu backend eski bo'lsa — lidlar 404ga ketadi.
- **`AMOCRM_WEBHOOK_URL`** prod/staging `.env`ga (real-time uchun). Lokalda bo'sh — localhost akkauntga yozilmasin.
- **AmoCRM Marketplace OAuth** (Instagram-style oson ulash) — kod ~1 kunlik, lekin AmoCRM moderatsiyasi kutiladi. Alohida task.

## Standing qoida

`back`/`admin` repolari **push qilinmaydi** — foydalanuvchi lokalda tekshirib keyin o'zi push qiladi. Istisno: `landing` (foydalanuvchi buyrug'i bilan push qilingan). Bir sessiya davomida backend bir necha bor rebuild/restart qilindi; migratsiyalar lokalda qo'llandi (prod'da deploy'da avto).
