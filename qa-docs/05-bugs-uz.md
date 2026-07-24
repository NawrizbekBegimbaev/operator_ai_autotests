# 05. Baglar jurnali — Admin (UI)

**Maqsad:** interfeysdan qo'lda o'tishda topilgan baglar shu yerga yoziladi.
**Loyiha qoidasi:** bagni faqat o'zimiz takrorlab (reproduce qilib) ko'rgach kiritamiz. Kod bo'yicha kuzatuvlar (hali takrorlanmaganlari) `03-questions-for-team.md` da yashaydi, bu yerda emas.

**Qanday kiritiladi:** quyidagi «Shablon»ni nusxa olib, «Baglar» bo'limiga qo'ying, raqam bering (BUG-XXX), maydonlarni to'ldiring, umumiy jadvalga qator qo'shing.

> **Til haqida:** bu — `05-bugs.md` (rus tili) faylining o'zbekcha nusxasi. Ikkala fayl ham bir xil baglarni saqlaydi; yangilaganda ikkalasini ham sinxron yuriting.

---

> ⚠️ **BUG-001…BUG-008 baglarining barchasi PRODUCTION da topilgan (23.07.2026).** Bu shoshilinchlikni oshiradi — nuqsonlarni haqiqiy foydalanuvchilar hozir ko'rib turibdi. Alohida jiddiy: BUG-002 (super-admin kirishi ochiq) prod da.
>
> **Jarayon bo'yicha ikki ogohlantirish:**
> 1. **Biz jangovar tizimda ma'lumot yaratdik/o'zgartirdik.** Ayrim baglar prodni o'zgartiruvchi amallar bilan takrorlangan: ROP yaratish (BUG-007), tarifni tahrirlash (BUG-008), ROPni deaktivatsiya qilish (BUG-006). Prodda test ROPlar va o'zgartirilgan tariflar qolgan bo'lishi mumkin — **topib tozalash** (yoki qaytarish) kerak, haqiqiy ma'lumotlarga xalaqit bermasin. Nima yaratilgan/o'zgartirilganini yozib qo'ying.
> 2. **Bundan buyon funksional tekshiruvlar (yaratish, tahrirlash, deaktivatsiya) staging/test da bajariladi, prodda emas** — loyiha qoidasiga ko'ra. Prodda faqat passiv kuzatuv (sahifani ochib ko'rish) mumkin, ma'lumotni o'zgartirmasdan. Agar staging muhiti yo'q bo'lsa — bu o'zi jamoaga savol ko'tarish uchun sabab (test AmoCRM/OnlinePBX bilan test stend kerak).

---

## Maydonlar izohi

| Maydon | Nima yoziladi |
| --- | --- |
| **Platforma** | Qayerda topildi: Web (brauzer), qaysi — Chrome / Firefox / Safari; OS |
| **Ilova** | Admin / Landing (admin uchun rolni aniqlang: Super-admin / ROP / Operator) |
| **Muhit** | staging / test / local. **Hech qachon prod emas** |
| **Tavsif** | Bir jumla — muammoning mohiyati (umumiy jadvalga tushadi) |
| **Qadamlar** | Noldan takrorlash yo'li, raqamlangan, istalgan odam takrorlay olsin |
| **Kutilgan natija** | Nima bo'lishi kerak edi |
| **Haqiqiy natija** | Aslida nima bo'ldi |
| **Ilova (attachment)** | Skrinshot / video / DevTools dagi so'rov-javob (fayl nomi yoki havola) |

**Muhimlik (P):** P1 — ishni bloklaydi · P2 — jiddiy, chetlab o'tish yo'li bor · P3 — kichik/kosmetik
**Holat:** 🔴 Yangi · 🟡 Ishda (dasturchida) · 🟢 Tuzatilgan · ✅ Tekshirilgan (yopilgan) · ⚪️ Bag emas / takrorlanmaydi

---

## Umumiy jadval

| № | Tavsif | Ilova / Rol | Muhimlik | Holat |
| --- | --- | --- | --- | --- |
| [BUG-001](#bug-001) | Parol maydonidagi ko'rsatish tugmasi — «показать» matni, aslida ikonka (ko'z) bo'lishi kerak | Admin — kirish ekrani | P3 | 🔴 Yangi |
| [BUG-002](#bug-002) | 🔒 Kirish ekranida super-admin login va paroli oldindan to'ldirilgan (`root` / standart parol), prodda ham | Admin — kirish ekrani | **P1** | 🔴 Yangi |
| [BUG-003](#bug-003) | Maydonlardagi matn vertikal markazda emas (yuqoriga siqilgan) — barcha formalardagi umumiy maydon nuqsoni | Admin — formalar (ROP yaratish, Parol tiklash, …) | P3 | 🔴 Yangi |
| [BUG-004](#bug-004) | «Telefon» maydoni harf va istalgan matnni qabul qiladi — format va `+998 xx xxx xx xx` maskasi tekshirilmaydi | Admin — Super-admin, «ROP yaratish» formasi | P2 | 🔴 Yangi |
| [BUG-005](#bug-005) | Parol maydonlarida kiritilgan parolni ko'rsatish tugmasi yo'q — parol kiritiladigan barcha formalarda | Admin — formalar (ROP yaratish, Parol tiklash, …) | P3 | 🔴 Yangi |
| [BUG-006](#bug-006) | 🔒 ROP deaktivatsiyasidan keyin ochiq sessiya tugamaydi — deaktivatsiya qilingan foydalanuvchi ishlashda davom etadi (~15 daqiqagacha) | Admin — avtorizatsiya / deaktivatsiya | P2 | 🔴 Yangi |
| [BUG-007](#bug-007) | Bitta telefon raqamiga bir nechta ROP yaratish mumkin — telefon unikal ekani tekshirilmaydi | Admin — Super-admin, ROP yaratish | P2 | 🔴 Yangi |
| [BUG-008](#bug-008) | Tarifni tahrirlashda «Narx» maydoni istalgan to'g'ri songa «Invalid input» beradi — narxni saqlab bo'lmaydi | Admin — Super-admin, tariflar muharriri | P2 | 🔴 Yangi |

---

## Shablon (shu yerdan nusxa oling)

```
### BUG-XXX. <qisqa nomi>

| Platforma | Ilova | Muhit | Tavsif |
| --- | --- | --- | --- |
| Web / Chrome / macOS | Admin — <rol> | staging | <bir jumla> |

**Muhimlik:** P?   **Holat:** 🔴 Yangi   **Sana:** KK.OO.YYYY

**Tavsif:**


**Qadamlar:**
1.
2.
3.

**Kutilgan natija:**


**Haqiqiy natija:**


**Ilova (attachment):**


**Bog'liqlik:** <Q-XX savoliga / Р-XX nomuvofiqligiga / qa-docs bo'limiga havola, agar bo'lsa>
```

---

## Baglar

<a id="bug-001"></a>
### BUG-001. Parolni ko'rsatish tugmasi ikonka o'rniga matn bilan chiqadi

| Platforma | Ilova | Muhit | Tavsif |
| --- | --- | --- | --- |
| Web / brauzer | Admin — kirish ekrani (avtorizatsiyadan oldin) | production | «Parol» maydonida ko'rinuvchanlik almashtirgichi ikonka (ko'z) o'rniga «показать» / «ko'rsatish» so'zi bilan chiqadi |

**Muhimlik:** P3 (kosmetik, funksiyaga ta'sir qilmaydi)   **Holat:** 🔴 Yangi   **Sana:** 23.07.2026

**Tavsif:**
Kirish sahifasida «Parol» maydonining o'ng tomonida kiritilgan parolni yashiradigan/ko'rsatadigan almashtirgich bor. Hozir u **matn** bilan chizilgan («показать», o'zbekcha lokalda — «ko'rsatish»). Umumiy qabul qilingan pattern va shablonning asl dizayni bo'yicha u yerda so'z emas, **ko'z ikonkasi** (ochiq ko'z / chizib tashlangan ko'z) bo'lishi kerak.

**Qadamlar:**
1. Admin kirish sahifasini oching (`/auth/jwt/sign-in`).
2. «Parol» maydonining o'ng qismiga qarang.

**Kutilgan natija:**
Maydonning o'ng qismida — ikonka (ko'z). Bosilganda parol ko'rsatiladi/yashiriladi, ikonka o'zgaradi (ochiq ↔ chizib tashlangan ko'z).

**Haqiqiy natija:**
Ikonka o'rniga «показать» matni. Almashtirilgach, koddan ko'rinishicha, matn «скрыть» / «yashirish»ga o'zgaradi.

**Ilova (attachment):**
`Снимок экрана — 2026-07-23 в 13.40.53.png`

**Bog'liqlik / koddagi joyi:**
- `project/admin/src/auth/view/jwt/jwt-sign-in-view.tsx:125` — `InputAdornment` ichida `{showPassword.value ? t('hide') : t('show')}` (matn) render qilinadi, u yerda `<Iconify>` ko'z ikonkasi kutiladi.
- Matnlar lokallardan olinadi: `src/locales/ru/auth.json` (`"show": "показать"`), `src/locales/uz/auth.json` (`"show": "ko'rsatish"`).
- Tuzatish: matnli belgilarni ikonkaga almashtirish (masalan `solar:eye-bold` / `solar:eye-closed-bold`), qulaylik uchun `aria-label` ni saqlab.

**QA izohi:** skrinshotda «Login» maydoniga `root` qo'yilgan — bu alohida muammo, BUG-002 sifatida kiritilgan.

---

<a id="bug-002"></a>
### BUG-002. 🔒 Kirish ekrani super-admin hisob ma'lumotlari bilan oldindan to'ldirilgan (prodda ham)

| Platforma | Ilova | Muhit | Tavsif |
| --- | --- | --- | --- |
| Web / brauzer | Admin — kirish ekrani (avtorizatsiyadan oldin) | **production** (prod-saytda takrorlangan) | Kirish sahifasi ochilganda «Login» va «Parol» maydonlari allaqachon super-administratorning haqiqiy standart hisob ma'lumotlari bilan to'ldirilgan (`root` / standart parol). «Kirish»ni bosish kifoya |

**Muhimlik:** P1 — xavfsizlik muammosi   **Holat:** 🔴 Yangi   **Sana:** 23.07.2026

**Tavsif:**
Kirish formasi **oldindan to'ldirilgan** login va parol bilan ochiladi. Bu bo'sh pleysholderlar emas, balki frontend kodiga qattiq yozilgan ishchi standart qiymatlar: login `root`, parol — standart (8 belgi). `root` — bu **super-administrator** hisobi, u backend ishga tushganda avtomatik yaratiladi. Ya'ni kirish sahifasini ochgan har kim (jumladan prodda) super-admin sifatida bir bosishda, hech nima bilmasdan kira oladi.

Ikki tomonlama muammo:
1. **Frontend** formaga tayyor login/parolni qo'yadi (prodda ham).
2. **Backend** ishga tushganda super-adminni shu standart parol bilan yaratadi, va parol, ko'rinishidan, o'zgartirilmagan.

**Qadamlar:**
1. Admin prod-saytini, kirish sahifasini oching.
2. Hech nima kiritmasdan «Login» va «Parol» maydonlariga qarang — ular allaqachon to'ldirilgan.
3. (Prodda ruxsatsiz bajarmang) «Kirish»ni bosing.

**Kutilgan natija:**
«Login» va «Parol» maydonlari **bo'sh**. Formada hech qanday standart hisob ma'lumotlari yo'q. Super-admin standart paroli har qanday muhitda unikalga o'zgartirilgan va faqat maxfiy joyda (`.env`) saqlanadi, kodda emas.

**Haqiqiy natija:**
Maydonlar ochilishi bilanoq `root` / standart parol bilan to'ldirilgan; super-admin sifatida parolni bilmasdan kirish mumkin. Productionda takrorlanadi.

**Ilova (attachment):**
`Снимок экрана — 2026-07-23 в 13.44.10.png`

**Bog'liqlik / koddagi joyi:**
- `project/admin/src/auth/view/jwt/jwt-sign-in-view.tsx:52-55` — `defaultValues: { username: 'root', password: '<замаскировано — см. Р-17>' }`. Bo'sh bo'lishi kerak (`username: '', password: ''`).
- Backend: ishga tushganda standart super-admin yaratiladi (`EnsureDefaultSuperAdmin`, `internal/app/app.go`) — prodda uning paroli o'zgartirilganiga ishonch hosil qilish kerak.
- Ilgari `01-project-analysis.md` da **Р-17** nomuvofiqligi va **R-5** xatari sifatida qayd etilgan.

**QA izohi — shoshilinchlik:** bu kosmetika emas. Prodda oldindan to'ldirish va standart parol tirik ekan, super-admin kirishi amalda ochiq. Umumiy bag navbatidan tashqarida eskalatsiya qilishni tavsiya qilaman va parallel tekshirish: (1) prodda haqiqiy `root` paroli o'zgartirilganmi; (2) uning ostida begonalar kirmaganmi (kirish loglari). «Prodda haqiqatan kirish mumkinmi» tekshiruvini **faqat mas'ul ruxsati bilan** bajaring — jangovar tizimga o'zboshimchalik bilan kirishni sinamang.

---

<a id="bug-003"></a>
### BUG-003. Maydonlardagi matn markazda emas, yuqoriga siqilgan — barcha formalardagi umumiy maydon nuqsoni

| Platforma | Ilova | Muhit | Tavsif |
| --- | --- | --- | --- |
| Web / brauzer | Admin — bir nechta forma (Super-admin va b.) | production | Maydonlardagi matn (pleysholder/kiritilgan qiymat) vertikal markaz o'rniga yuqori chetga tekislangan. Bitta umumiy maydon uslub nuqsoni, shu maydonlar ishlatilgan barcha formalarda ko'rinadi |

**Muhimlik:** P3 (kosmetik)   **Holat:** 🔴 Yangi   **Sana:** 23.07.2026

**Tavsif:**
Kiritish maydonlari vizual balandroq, ichidagi matn esa vertikal markaz o'rniga **yuqori** qismga siqilgan — maydonlar «yarim bo'sh» va tartibsiz ko'rinadi. Bu **bitta formaning muammosi emas**, maydon komponentining umumiy nuqsoni: u ishlatilgan hamma joyda takrorlanadi.

**Tasdiqlangan joylar (o'tish davomida yangilanadi):**
- «ROP yaratish» — barcha maydonlar (Ism, Familiya, Telefon, Parol, Login, Kompaniya nomi, Tarif). Skrinshot `Снимок экрана — 2026-07-23 в 13.46.22.png`.
- «Parol tiklash» — «Yangi parol», «Yangi parolni takrorlang» maydonlari. Skrinshot `Снимок экрана — 2026-07-23 в 13.54.09.png`.
- «AmoCRM ulanishi» — barcha maydonlar (Domain, Client ID, Client secret, Redirect URI, Access token, Lead source). Skrinshot `Снимок экрана — 2026-07-23 в 14.01.09.png`.
- _(tekshirib qo'shish: «Operator yaratish», «OnlinePBX ulanishi», tahrirlash oynalari)_

**Qadamlar (parol tiklash misolida):**
1. Super-admin (yoki ROP) sifatida kiring.
2. Operatorlar kartochkasi/jadvalini oching, istalgan foydalanuvchida «Parol tiklash»ni chaqiring.
3. «Yangi parol» / «Yangi parolni takrorlang» maydonlaridagi pleysholder matni tekislanishiga qarang.

**Kutilgan natija:**
Matn (pleysholder va kiritilgan qiymat) maydon vertikal markaziga tekislangan; maydon balandligi mazmuniga mos.

**Haqiqiy natija:**
Matn yuqori chetga siqilgan; maydonlar balandroq ko'rinadi, pastda bo'sh joy. Tekshirilgan barcha formalarda bir xil.

**Ilova (attachment):**
`Снимок экрана — 2026-07-23 в 13.46.22.png` (ROP yaratish), `Снимок экрана — 2026-07-23 в 13.54.09.png` (Parol tiklash)

**Bog'liqlik / qayerni qarash kerak:**
- Umumiy maydon komponenti — `project/admin/src/components/hook-form/` (`Field.Text` → MUI `TextField`). Nuqson barcha formalarda bo'lgani uchun, tuzatish **bitta joyda** kerak — shu komponent uslubida (yoki mavzuda), har bir formada emas.
- Ehtimol, mazmunni vertikal markazlashtirmasdan balandlik oshirilgan (`minHeight`/`padding`).

**QA izohi:** nuqson umumiy — maydon komponentidagi bitta tuzatish uni barcha formalarda birdaniga yopadi. Fiksni tekshirishda «Tasdiqlangan joylar» ro'yxatidagi barcha formalardan o'ting.

---

<a id="bug-004"></a>
### BUG-004. «Telefon» maydoni harf va istalgan matnni qabul qiladi (format tekshirilmaydi)

| Platforma | Ilova | Muhit | Tavsif |
| --- | --- | --- | --- |
| Web / brauzer | Admin — Super-admin, «ROP yaratish» oynasi | production | «Telefon» maydoni ixtiyoriy matnni (harflar, belgilar) qabul qiladi; format va `+998 xx xxx xx xx` kiritish maskasi tekshirilmaydi |

**Muhimlik:** P2 (tizimga noto'g'ri ma'lumotni o'tkazib yuboradi)   **Holat:** 🔴 Yangi   **Sana:** 23.07.2026

**Tavsif:**
ROP yaratish formasida «Telefon» maydoni kiritilgan qiymat formatini tekshirmaydi. Harflar («выфвыфвыфвфывфвы»), bo'shliqlar, istalgan belgilarni kiritish mumkin — forma buni qabul qiladi. `+998 xx xxx xx xx` formatida o'zbek raqami kutiladi, boshqa belgilar kiritilmasligi kerak (yoki maska bilan bloklanadi, yoki validatsiya bilan kesiladi).

**Qadamlar:**
1. Super-admin sifatida kiring, ROP bo'limini oching.
2. Yangi ROP yaratishni bosing → «ROP yaratish».
3. «Telefon» maydoniga harflar kiriting, masalan `выфвыфвыф`.
4. Qolgan majburiy maydonlarni to'g'ri to'ldirib «Yaratish»ni bosing.

**Kutilgan natija:**
Maydon faqat `+998 xx xxx xx xx` formatidagi telefonni qabul qiladi. Harflar va begona belgilar yo kiritilmaydi (maska), yo forma validatsiya xatosini ko'rsatadi va noto'g'ri telefon bilan ROP yaratishga ruxsat bermaydi.

**Haqiqiy natija:**
Maydon harflar jumladan istalgan matnni qabul qiladi. Format validatsiyasi yo'q — faqat maydon bo'sh emasligi tekshiriladi.

**Ilova (attachment):**
`Снимок экрана — 2026-07-23 в 13.48.33.png`

**Bog'liqlik / koddagi joyi:**
- `project/admin/src/sections/users/user-list-view.tsx:222` — `phone: z.string().trim().min(1, ...)`: faqat bo'sh emasligi tekshiriladi, regex/maska yo'q.
- Maydon oddiy `Field.Text name="phone"` bilan render qilinadi (~1597, ~1649 qatorlar) — kiritish maskasisiz.
- Tuzatish: zod-sxemaga format tekshiruvini qo'shish (`+998` + 9 raqam uchun regex) va/yoki maydonga kiritish maskasi. Formatni backendda ham sinxron tekshirish maqsadga muvofiq (klientdagi validatsiya API orqali chetlab o'tiladi).

**QA izohi:**
1. Xuddi shu «Telefon» maydonini **«Operator yaratish»** formasida va **tahrirlash** oynalarida tekshiring — telefon validatsiyasi, koddan ko'rinishicha, umumiy, nuqson u yerda ham takrorlanadi.
2. Alohida backendda tekshiring: so'rov to'g'ridan-to'g'ri yuborilsa, API noto'g'ri telefonni qabul qiladimi (klient validatsiyasi ma'lumotni o'zi himoya qilmaydi).
3. Jamoadan aniq talab qilinadigan formatni aniqlang (faqat `+998`? `+998` siz, lokal raqamlarga ruxsatmi?) — bu regexga ta'sir qiladi. Kerak bo'lsa `03-questions-for-team.md` da savol sifatida rasmiylashtiring.

---

<a id="bug-005"></a>
### BUG-005. Parolni ko'rsatish tugmasi yo'q — parol kiritiladigan barcha formalarda

| Platforma | Ilova | Muhit | Tavsif |
| --- | --- | --- | --- |
| Web / brauzer | Admin — bir nechta forma | production | Parol maydonlarida ko'rinuvchanlik almashtirgichi (ko'z ikonkasi) yo'q — admin qanday parol kiritganini tekshira olmaydi. Parol kiritiladigan barcha formalarda ko'rinadi |

**Muhimlik:** P3 (qulaylik / usability)   **Holat:** 🔴 Yangi   **Sana:** 23.07.2026

**Tavsif:**
Parol maydonlari doim nuqtalar bilan yashirilgan, yonida «ko'rsatish» tugmasi (ko'z ikonkasi) yo'q. Parolni belgilaydigan kishi (Super-admin ROP yaratadi; Super-admin/ROP foydalanuvchi parolini tiklaydi) aynan xohlagan narsasini kiritganiga ishonch hosil qila olmaydi — bu parol keyin odamga uzatiladi. Kirish ekranidagidek ko'rinuvchanlik almashtirgichi kerak (u yerda bor, garchi matn bilan bo'lsa ham — BUG-001 ga qarang). Bu **bitta formaning muammosi emas**: parol maydoni hamma joyda almashtirgichsiz chizilgan.

**Tasdiqlangan joylar (o'tish davomida yangilanadi):**
- «ROP yaratish» — «Parol» maydoni. Skrinshot `Снимок экрана — 2026-07-23 в 13.51.44.png`.
- «Parol tiklash» — «Yangi parol» va «Yangi parolni takrorlang» maydonlari. Skrinshot `Снимок экрана — 2026-07-23 в 13.56.56.png`.
- _(tekshirib qo'shish: «Operator yaratish», tahrirlash oynalari)_

**Qadamlar (parol tiklash misolida):**
1. Super-admin (yoki ROP) sifatida kiring.
2. Istalgan foydalanuvchida «Parol tiklash»ni chaqiring.
3. «Yangi parol» / «Yangi parolni takrorlang»ga qiymat kiriting.
4. Kiritilgan qiymatni ko'rishga urinib ko'ring.

**Kutilgan natija:**
Har bir parol maydonida kiritilgan qiymatni ko'rsatish/yashirish uchun tugma (ko'z ikonkasi) bor.

**Haqiqiy natija:**
Hech bir formada almashtirgich yo'q; parol doim nuqtalar bilan yashiriladi, uni tekshirib bo'lmaydi.

**Ilova (attachment):**
`Снимок экрана — 2026-07-23 в 13.51.44.png` (ROP yaratish), `Снимок экрана — 2026-07-23 в 13.56.56.png` (Parol tiklash)

**Bog'liqlik / koddagi joyi:**
- ROP yaratish — `project/admin/src/sections/users/user-list-view.tsx:1598` — `<Field.Text name="password" type="password" />` almashtirgichsiz.
- Parol tiklash — `project/admin/src/sections/users/user-reset-password-dialog.tsx:113,117` — ikkala maydon ham `type="password"` almashtirgichsiz.
- AmoCRM-konfigning maxfiy maydonlari ham (`client_secret`, `access_token`, ~1762, ~1764) `type="password"` almashtirgichsiz — maxfiy qiymatlar uchun ko'rsatish, aksincha, kerak bo'lmasligi mumkin; aniqlashtirilsin.
- Tuzatish: parol maydoni komponentiga ko'z ikonkasi bilan `InputAdornment` va `showPassword` holatini qo'shish (`jwt-sign-in-view.tsx` dagidek), yaxshisi — qayta ishlatiladigan maydon darajasida bir marta. Matn emas, ikonka ishlating (BUG-001 ni takrorlamaslik uchun).

**QA izohi:** nuqson umumiy — agar almashtirgich qayta ishlatiladigan parol maydoni darajasida qilinsa, u barcha formalarda birdaniga paydo bo'ladi. Fiksni tekshirishda «Tasdiqlangan joylar»dagi barcha formalardan o'ting. Integratsiyalarning maxfiy maydonlarida ko'rsatish kerakmi — jamoa bilan alohida hal qiling.

---

<a id="bug-006"></a>
### BUG-006. 🔒 ROP deaktivatsiyasi allaqachon ochilgan sessiyani tugatmaydi

| Platforma | Ilova | Muhit | Tavsif |
| --- | --- | --- | --- |
| Web / brauzer | Admin — avtorizatsiya / foydalanuvchini deaktivatsiya qilish | production | ROP deaktivatsiyasidan keyin kirish bloklanadi (to'g'ri), lekin allaqachon kirgan foydalanuvchi joriy access-token muddati tugaguncha (~15 daqiqagacha) to'liq ishlashda davom etadi |

**Muhimlik:** P2 (kirish nazorati buzilishi, ammo oyna ~15 daq bilan cheklangan)   **Holat:** 🔴 Yangi   **Sana:** 23.07.2026

**Tavsif:**
Deaktivatsiya darhol ta'sir qilmaydi. Deaktivatsiya qilingan ROPning yangi kirishi to'g'ri taqiqlanadi. Lekin agar ROP deaktivatsiyadan **oldin sessiya ochgan** bo'lsa, u tizimdan hech nima bo'lmagandek foydalanishda davom etadi — sahifalar ochiladi, so'rovlar o'tadi. Kirish faqat uning joriy access-tokeni muddati tugaganda (standart bo'yicha 15 daqiqadan keyin) uziladi, shundan so'ng tokenni yangilash urinishi bloklanadi va foydalanuvchi chiqarib yuboriladi.

Sabab (koddan) — uch omil birgalikda:
1. Har so'rovdagi avtorizatsiya tekshiruvi (`RequireAuth`) faqat token imzosi va amal muddatini tekshiradi, foydalanuvchi `IsActive` ni **solishtirmaydi**.
2. Deaktivatsiya allaqachon berilgan sessiyalarni **bekor qilmaydi** (`auth_sessions` bekor qilinmaydi).
3. Faollik faqat kirishda va tokenni yangilashda tekshiriladi — yangilash esa faqat access-token muddati tugaganda bo'ladi. U tirik ekan (15 daq gacha), faollik tekshiruvi umuman bo'lmaydi.

**Qadamlar:**
1. ROP sifatida tizimga kiring (sessiya faol), tabni ochiq qoldiring.
2. Boshqa brauzer/oynada Super-admin sifatida shu ROPni deaktivatsiya qiling.
3. ROP tabiga qayting va ishlashda davom eting: sahifalar oching, amallar bajaring.

**Kutilgan natija:**
Deaktivatsiyadan keyin kirish **darhol** (yoki soniyalar ichida) to'xtaydi: keyingi so'rovning o'zi rad etiladi, foydalanuvchi tizimdan chiqariladi. «Ishdan bo'shatilgan»ning deaktivatsiyasi darhol amal qilishi kerak.

**Haqiqiy natija:**
Deaktivatsiya qilingan ROP joriy access-token muddati tugaguncha — ~15 daqiqagacha to'liq ishlashda davom etadi. Shu vaqt davomida uning so'rovlari o'tadi.

**Ilova (attachment):**
_(video/skrinshotlar ixtiyoriy — videoda ko'rgazmali)_

**Bog'liqlik / koddagi joyi:**
- `project/back/internal/controller/http/middleware.go:142` — `ParseAccessToken(token)`: faqat JWT haqiqiyligi tekshiriladi, har so'rovda foydalanuvchi `IsActive` solishtirilmaydi.
- `project/back/internal/usecase/user/service.go:282` — deaktivatsiya `IsActive=false` qo'yadi, lekin faol sessiyalarni (`auth_sessions`) bekor **qilmaydi**.
- `project/back/internal/usecase/auth/service.go:89` (Login) va `:208` (Refresh) — faollik tekshiriladi, shuning uchun deaktivatsiyadan keyin kirish va tokenni yangilash bloklanadi (bu «15 daqiqadan keyin chiqarib yuboradi»ni beradi).
- `project/back/internal/config/config.go:64` — `AUTH_ACCESS_TOKEN_TTL_MINUTES` = 15 (ekspozitsiya oynasi).

**Tuzatish variantlari (jamoa uchun):**
- Deaktivatsiyada foydalanuvchining barcha `auth_sessions` ini bekor qilish — u holda access-token muddati tugagach refresh aniq muvaffaqiyatsiz bo'ladi (oyna baribir 15 daq gacha).
- Yoki `RequireAuth` da har so'rovda `IsActive` ni solishtirish (DB/kesh so'rovi evaziga) — u holda uzilish darhol.
- Yoki access-token TTL ni qisqartirish va/yoki bekor qilingan tokenlarning «qora ro'yxati»ni qo'shish.

**Hujjat bilan bog'liqlik / jamoadan aniqlash:**
- `MVP-Scope.md` da «Account deactivation (ROP deactivates operator, Admin deactivates ROP)» **Open** deb belgilangan — ya'ni funksiya rasman hali tayyor emas. Ehtimol, sessiyani darhol uzish shunchaki tugatilmagan. **Jamoadan aniqlang**, deaktivatsiya tezligiga talab qanday bo'lishi kerak (darhol / ~15 daq oyna maqbulmi). Kerak bo'lsa `03-questions-for-team.md` da savol sifatida rasmiylashtiring.
- Xuddi shu mexanizm **operator deaktivatsiyasiga** ham tegishli (nafaqat ROP). Tekshiring va takrorlansa, shu yerga qo'shing.

---

<a id="bug-007"></a>
### BUG-007. Bitta telefon raqamiga bir nechta ROP yaratish mumkin

| Platforma | Ilova | Muhit | Tavsif |
| --- | --- | --- | --- |
| Web / brauzer | Admin — Super-admin, ROP yaratish | production | Tizim bir xil telefon raqamiga bir nechta har xil ROP yaratishga ruxsat beradi — telefon unikalligi tekshirilmaydi |

**Muhimlik:** P2 (ma'lumotlar yaxlitligining buzilishi)   **Holat:** 🔴 Yangi   **Sana:** 23.07.2026

**Tavsif:**
ROP yaratishda telefon unikallikka tekshirilmaydi — bir xil raqam bilan ikki va undan ortiq har xil ROP yaratish mumkin. Taqqoslash uchun: login (`username`) unikal va uni qayta band qilib bo'lmaydi, telefon esa yo'q.

**Qadamlar:**
1. Super-admin sifatida kiring, ROP bo'limini oching.
2. Telefon bilan ROP yarating, masalan `+998901112233` (login va boshqa maydonlar — istalgan unikal).
3. **Xuddi shu** telefon `+998901112233` bilan yana bir ROP yarating (login boshqa).
4. Ikkala ROP ham muvaffaqiyatli yaratiladi.

**Kutilgan natija:**
_(mahsulot qaroriga bog'liq — izohga qarang)_ Kutilishicha: allaqachon band telefon bilan ikkinchi ROP yaratishga urinishda tizim «telefon allaqachon ishlatilmoqda» xatosini ko'rsatadi va yozuvni yaratmaydi.

**Haqiqiy natija:**
Ikkala ROP ham bir xil telefon bilan hech qanday ogohlantirishsiz yaratiladi.

**Ilova (attachment):**
_(jadvalda bir xil telefonli ikki ROP skrinshoti)_

**Bog'liqlik / koddagi joyi:**
- `project/back/db/query/schema.sql:41` — `phone TEXT NOT NULL DEFAULT ''`: **`UNIQUE` cheklovi yo'q** (37-qatordagi `username` dan farqli, u unikal).
- `project/back/internal/usecase/auth/service.go:290` (`validateAccountInput`) — faqat telefon bo'sh emasligi tekshiriladi (304–305 qatorlar); dublikat tekshiruvi yo'q.
- Tuzatish: telefon unikalligini DB darajasida qo'shish (unique-indeks, raqam normalizatsiyasi bilan) va usecase/formada tushunarli xato.

**Hujjat bilan bog'liqlik / jamoadan aniqlash:**
- Rasmiy jihatdan «telefon unikal bo'lishi kerakmi» — **mahsulot qarori**. Ehtimol, telefon takrorlanishi mumkin deb o'ylangan (masalan, bitta kontakt bir necha ob'ektga). **Jamoadan aniqlang**: telefon unikal bo'lishi shartmi? Global (barcha foydalanuvchilar orasida) yoki faqat ROPlar orasida? Turli formatlangan raqamlarni (`+998 90 111 22 33` va `998901112233`) bir xil deb hisoblansinmi? Javobga unique-indeksdagi normalizatsiya ham bog'liq.
- **BUG-004** bilan bog'liq (u yerda ham — telefon format validatsiyasi yo'q). Agar unikallik kiritilsa, uni normalizatsiya qilingan raqam bo'yicha hisoblash kerak, bu esa yagona formatni talab qiladi (⇒ avval BUG-004 dagi formatni tuzatish mantiqan to'g'ri).
- Agar jamoa «telefon unikal bo'lishi shart emas» desa — bu bandni `03-questions-for-team.md` ga o'tkazing / «bag emas» sifatida yoping.

**QA izohi:** xuddi shuni **operator** yaratishda tekshiring — u yerda ham telefon unikalligi, ehtimol, tekshirilmaydi (umumiy mexanizm).

---

<a id="bug-008"></a>
### BUG-008. Tarif muharririda «Narx» maydoni istalgan to'g'ri sonni rad etadi («Invalid input»)

| Platforma | Ilova | Muhit | Tavsif |
| --- | --- | --- | --- |
| Web / brauzer | Admin — Super-admin, tariflar muharriri (`/dashboard/plans`) | production | Tarifni tahrirlash formasida «Narx (so'm/oy)» maydoni to'g'ri son (masalan `412`) kiritilganda «Invalid input» xatosini ko'rsatadi. Narxni saqlab bo'lmaydi |

**Muhimlik:** P2 (funksiya buzilgan — tarif narxini belgilab bo'lmaydi)   **Holat:** 🔴 Yangi   **Sana:** 23.07.2026

**Tavsif:**
Tarifni tahrirlashda «Narx (so'm/oy) — 0 = «Shartnomaviy»» maydoniga istalgan bo'sh bo'lmagan son kiritilishi «Invalid input» validatsiya xatosini keltiradi, garchi qiymat to'g'ri bo'lsa ham. Natijada belgilangan narx bilan tarifni saqlab bo'lmaydi.

Sabab (koddan): `type="number"` maydoni react-hook-form da qiymatni **satr** sifatida qaytaradi (`"412"`), zod-sxema esa yo haqiqiy son, yo bo'sh satrni kutadi — sonli satr ikkalasiga ham to'g'ri kelmaydi, shundan «Invalid input». Ya'ni faqat 412 emas, **istalgan bo'sh bo'lmagan son** rad etiladi.

**Qadamlar:**
1. Super-admin sifatida kiring, `/dashboard/plans` ni oching.
2. Istalgan tarifni tahrirlashni oching (masalan «Tahlil»).
3. «Narx (so'm/oy)» maydoniga son kiriting, masalan `412`.
4. Maydonga qarang / «Saqlash»ni bosing.

**Kutilgan natija:**
Son to'g'ri narx sifatida qabul qilinadi; forma saqlanadi. `0` «Shartnomaviy» deb talqin qilinadi.

**Haqiqiy natija:**
Maydon ostida «Invalid input», ramka qizil, «Saqlash» tugmasi nofaol — hech qanday son bilan saqlab bo'lmaydi.

**Ilova (attachment):**
`BUG - 008.png`

**Bog'liqlik / koddagi joyi:**
- `project/admin/src/sections/plans/plans-view.tsx:51` — `price: z.union([z.number().min(0, ...), z.literal('')])`: haqiqiy son yoki `''` kutadi.
- `project/admin/src/sections/plans/plans-view.tsx:252` — `<Field.Text name="price" ... type="number" />`: `valueAsNumber`/koersiyasiz satr qaytaradi.
- Tuzatish: qiymatni songa keltirish — yo sxemada `z.coerce.number()` (bo'sh qiymat bilan ehtiyot bo'ling: `z.union([z.literal(''), z.coerce.number().min(0)])` yoki oldindan `transform`), yo maydonga ro'yxatdan o'tkazishda `valueAsNumber` berish. Fiksdan keyin `0` = «Shartnomaviy» to'g'ri saqlanishini tekshiring.

**QA izohi:**
1. Bu zod-union orqali sonli maydonli yagona formami? Boshqa sonli maydonlarni tekshiring (masalan operatordagi «Maosh» / `salary` — u yerda `z...positive`, kiritish ham satr bo'lib ketishi mumkin). Takrorlansa — bir xil sabab (sonli maydonlar koersiya qilinmaydi).
2. `0` (Shartnomaviy) qiymati saqlanishini tekshiring — bo'sh qiymat `z.literal('')` ga to'g'ri keladi, `"0"` satri sifatida kiritilgan `0` esa, ehtimol, «Invalid input» beradi.
