# OperatorAI — Ish jurnali v2 (birinchi jurnaldan keyin)

**Muddat:** 9 Iyul 2026 (davomi)
**Repolar:** `admin` (React), `back` (Go)
**Holat:** build / test / lint — hammasi yashil (FE tsc 0)

**Jami:** 12 task · Backend/DB: 8 · Frontend/UI: 3 · Tahlil/diagnostika: 3 · Bug tuzatildi: 3

Bu jurnal — `WORK_LOG.md` (36 task) yaratilgandan **keyingi** ishlar. Asosiy mavzu: AmoCRM leadlarini real qo'ng'iroq oqimiga ulash, avtomatlashtirish va topilgan xatolarni tuzatish.

Teglar: **BE** = Backend · **FE** = Frontend · **UI** = interfeys · **DB** = ma'lumotlar bazasi · **OPS** = DevOps

---

## 1 · AmoCRM ulanish va sinxronlash — 4 task

Real AmoCRM akkaunti ulandi (blitznemistili.amocrm.ru) va leadlar tizimga oqib kela boshladi.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 1.1 | **AmoCRM configni qayta ulash (409 fix)** | FE, UI | Config allaqachon bo'lsa forma har safar `POST` (create) yuborardi → `409 konflikt`. Endi mavjud config bo'lsa `PATCH` (update) qiladi. Maxfiy maydonlar (client_id/secret/token) backend javobida qaytmagani uchun — bo'sh qoldirilsa eskisi o'chib ketmaydigan qilindi (faqat yozilgani yuboriladi). |
| 1.2 | **Biriktirishda avto lead-sync** | BE | Ilgari leadlar faqat "Mezonlar"dagi yashirin pipeline-tanlashda yuklanardi (chalkash UX). Endi ROP operatorni pipeline'ga biriktirsa — o'sha pipeline leadlari AmoCRM'dan avtomatik tortiladi. Yangi `SyncPipelineLeadsForROP` + `PipelineLeadSyncer` interfeysi. |
| 1.3 | **Davriy avto-sync (scheduler)** | BE, OPS | Backend har 2 daqiqada (sozlanadi: `lead_sync_interval`) operatorlarga biriktirilgan har bir pipeline uchun AmoCRM'dan yangi/o'zgargan leadlarni tortadi. Outbound so'rov — localhost'da ham ishlaydi, webhook/ochiq domen shart emas. Startup'da darrov bir marta ishlaydi, ctx bilan to'xtaydi, panic-safe. |
| 1.4 | **Operator "Calls" ro'yxati scoping** | BE, DB | Operator ko'radigan lead ro'yxati endi faqat **o'ziga biriktirilgan pipeline** leadlarini ko'rsatadi + yopilganlar yashirin. Query'ga operator-allowlist va `exclude_closed` parametrlari qo'shildi. ROP/superadmin ko'rinishi o'zgarmaydi. |

---

## 2 · Qo'ng'iroq navbati sifati — 1 task

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 2.1 | **Yopilgan leadlarni navbatdan chiqarish** | BE, DB | AmoCRM API pipelinening HAMMA leadini qaytaradi (yopilganlar ham). Navbat 138 leaddan 129 tasi "Закрыто и не реализовано" bo'lganini sanardi (107 ta). Endi navbat AmoCRM terminal statuslarini (142 = yutildi, 143 = yo'qotildi) chiqarib tashlaydi → faqat **9 tirik lead**. Operator o'lik leadlarga qo'ng'iroq qilmaydi. |

---

## 3 · Xato va bug tuzatishlar — 3 task

Sinov paytida topilgan jiddiy xatolar.

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 3.1 | **Cheksiz polling loop (runaway)** | FE, UI | Qo'ng'iroq modalida sessiya holati `GET /calling/sessions/:id` orqali kuzatilardi. `useEffect` `session` obyektiga bog'langan + ichida `setSession` chaqirilardi → har javob effektni qayta ishga tushirib, 3s kutmasdan darrov qayta so'rov → sekundiga yuzlab so'rov (1700+), backend bosildi. Fix: dependency `session?.id` (barqaror) ga o'tkazildi — endi haqiqatan har 3 sekundda. |
| 3.2 | **Dial 500 (OnlinePBX call_url)** | BE | Qo'ng'iroq boshlashda `500 "foydalanuvchi amali bajarilmadi"`. Sabab: `CallDeal` `call_url` ni majburiy qilardi, ammo u **ixtiyoriy** (client bo'sh bo'lsa api2.onlinepbx.ru default qiladi). Config'da domen+token bor, call_url bo'sh edi → noto'g'ri rad. Fix: faqat token + domen majburiy. |
| 3.3 | **Qo'ng'iroq xatolarini to'g'ri map qilish** | BE | Call xatolari generic `500` bergan. Endi aniq: OnlinePBX xatosi → `502 "qo'ng'iroqni amalga oshirib bo'lmadi"`, sozlanmagan → `409` (aniq xabar), yomon telefon → `400`. Operator sababni ko'radi. |

---

## 4 · Tahlil va diagnostika — 3 task

| # | Task | Teg | Tafsilot |
|---|------|-----|----------|
| 4.1 | **Lead oqimi tekshiruvi** | Tahlil | AmoCRM ulanganidan keyin nima sinxronlangani DB'dan tasdiqlandi: 17 pipeline + formalar keldi, leadlar `amocrm_leads`ga tushdi. Yangi qo'shilgan 3 lead avto-sync bilan (task 1.3) o'zi kelishini tekshirildi. |
| 4.2 | **"Navbat 0" diagnostikasi** | Tahlil | Navbat bo'sh ko'rinishi — leadlar oldingi testda skip qilingani uchun `next_call_at` kelajakka surilgani aniqlandi (yo'qolmagan, vaqtincha rejalashtirilgan). |
| 4.3 | **Real qo'ng'iroq rad sababi** | Tahlil | Dial fix'dan keyin real call urinildi va OnlinePBX aniq sabab qaytardi: **`4001 user is disabled`** — operator extension'i OnlinePBX panelida o'chirilgan. Auth/token/domen ishlaydi ✓; qolgani telefoniya sozlamasi (panelda extension yoqish). |

---

## Kutilayotgan tashqi qadamlar (kod tayyor)

Kod tomondan oqim to'liq ulangan. Real qo'ng'iroq uchun tashqi sozlamalar kerak:

- **OnlinePBX** — operator extension (masalan 4001) panelida **yoqilishi** kerak (hozir disabled). Auth allaqachon ishlaydi.
- **Gemini** — AI API key (transkripsiya + maydon/status ajratish uchun). Kalitsiz call "dialing"da qoladi, tahlil bosqichiga o'tmaydi.
- **AmoCRM** — ulangan ✓. Real-time uchun (ixtiyoriy) prod domenida webhook; hozir 2 daqiqalik avto-sync yetarli.

## Texnik izoh

Barcha backend o'zgarishlar `make run` (yangi kompilyatsiya) bilan yoki restart bilan faollashadi. Bir sessiya davomida bir necha bor backend restart qilindi; ikkala repo ham build/test yashil holatda.
