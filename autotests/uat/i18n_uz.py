"""Узбекская локализация ежедневного UAT-отчёта (латиница).

Отчёт читают люди без IT-образования, поэтому формулировки бытовые:
никаких «assert», «pytest» и «endpoint» — только «tekshirildi», «ochiladi»,
«ishlayapti».
"""

from __future__ import annotations


ROLES_UZ: dict[str, str] = {
    "Система": "Tizim",
    "Общий путь ролей": "Barcha rollar uchun umumiy yo'l",
    "Посетитель Landing": "Landing sahifasi tashrifchisi",
    "Super-admin": "Super-admin",
    "ROP": "ROP (bo'lim rahbari)",
    "Operator": "Operator",
}

STATE_UZ: dict[str, str] = {
    "passed": "O'tdi",
    "failed": "O'tmadi",
    "not_run": "Bajarilmadi",
    "blocked_defect": "Ma'lum xatolik sababli to'xtatilgan",
}

STATE_ICON: dict[str, str] = {
    "passed": "✅",
    "failed": "❌",
    "not_run": "⚠️",
    "blocked_defect": "⛔",
}

STATE_PLAIN_UZ: dict[str, str] = {
    "passed": "Tekshirildi va ishlayapti.",
    "failed": "Tekshirildi, lekin kutilgandek ishlamadi. Ko'rib chiqish kerak.",
    "not_run": "Bugun umuman tekshirilmadi.",
    "blocked_defect": "Avvaldan ma'lum xatolik tuzatilmagani uchun tekshirilmadi.",
}

PRIORITY_UZ: dict[str, str] = {
    "P0": "P0 — eng muhim",
    "P1": "P1 — muhim",
    "P2": "P2 — o'rtacha",
}

SUMMARY_LABELS_UZ: dict[str, str] = {
    "title": "Operator AI — kunlik tekshiruv hisoboti",
    "generated_at": "Hisobot sanasi va vaqti (Toshkent)",
    "verdict": "Umumiy xulosa",
    "verdict_green": "Hammasi joyida — bugun tekshirilgan barcha funksiyalar ishlayapti",
    "verdict_red": "Diqqat talab qiladi — quyidagi funksiyalarda muammo bor",
    "passed": "Tekshirildi va ishlayapti",
    "failed": "Ishlamadi (muammo bor)",
    "not_ready": "Bugun tekshirilmadi",
    "blocked": "Ma'lum xatolik sababli to'xtatilgan",
    "total": "Ro'yxatdagi jami tekshiruvlar",
    "duration": "Tekshiruvga ketgan vaqt",
    "by_role": "Rollar bo'yicha",
    "problems": "Diqqat talab qiladigan tekshiruvlar",
    "known_defects": "Ma'lum xatoliklar (dasturchilar tuzatishi kutilmoqda)",
    "no_problems": "Muammoli tekshiruvlar yo'q.",
}

SHEET_TITLES_UZ: dict[str, str] = {
    "summary": "Umumiy natija",
    "cases": "Tekshiruvlar",
    "defects": "Ma'lum xatoliklar",
    "statuses": "Statuslar izohi",
}

# Подсказка к колонке результата: всплывает при наведении на заголовок.
RESULT_HINT_UZ = "\n".join(
    f"{STATE_ICON[state]} {STATE_UZ[state]} — {STATE_PLAIN_UZ[state]}"
    for state in ("passed", "failed", "not_run", "blocked_defect")
)

STATUS_COLUMNS_UZ: tuple[str, ...] = (
    "Status (AmoCRM nomi)",
    "Ruscha",
    "Ma'nosi",
    "Navbatga tushadimi",
    "Navbatdagi o'rni",
    "Tanib olish so'zi",
)

# Источник правды — project/back/internal/usecase/calling/status_class.go
# (классы и порядок распознавания) и qa-docs/02-lead-status-glossary.md.
# Порядок строк = порядок выдачи лидов оператору.
LEAD_STATUSES_UZ: tuple[dict[str, str], ...] = (
    {
        "status": "Bugun keladi",
        "ru": "Придёт сегодня",
        "meaning": (
            "Mijoz bugun kelishini tasdiqlagan — eng \"issiq\" lid. "
            "Tashrifdan 60 daqiqa oldin beriladi; tashrif vaqti "
            "to'ldirilmagan bo'lsa, ish kuni boshidan (08:00) beriladi."
        ),
        "in_queue": "Ha",
        "rank": "1",
        "keyword": "bugun",
    },
    {
        "status": "Keyingi qo'ng'iroq vaqti",
        "ru": "Назначен перезвон",
        "meaning": (
            "Mijoz aniq vaqtda qayta qo'ng'iroq qilishni so'ragan. "
            "Belgilangan vaqt kelganda navbatga tushadi. Diqqat: vaqt "
            "to'ldirilmasa, lid navbatga umuman tushmaydi."
        ),
        "in_queue": "Ha",
        "rank": "2",
        "keyword": "keyingi + qongiroq",
    },
    {
        "status": "Chala gaplashdi",
        "ru": "Разговор не завершён",
        "meaning": (
            "Suhbat boshlangan, lekin oxiriga yetmagan: aloqa uzilgan yoki "
            "mijoz band bo'lgan. Oxirgi qo'ng'iroqdan 60 daqiqa o'tgach "
            "qaytadi; urinishlar soni cheklanmagan."
        ),
        "in_queue": "Ha",
        "rank": "3",
        "keyword": "chala",
    },
    {
        "status": "Ko'tarmadi",
        "ru": "Не берёт трубку",
        "meaning": (
            "Bog'lanib bo'lmadi. Har 180 daqiqada qayta beriladi, jami 4 ta "
            "urinish (urinishlar kunlar bo'ylab saqlanadi). 4 urinishdan "
            "keyin lid avtomatik ravishda \"Sifatsiz\" bo'ladi."
        ),
        "in_queue": "Ha",
        "rank": "4",
        "keyword": "kotarmadi",
    },
    {
        "status": "Yangi lid",
        "ru": "Новый лид",
        "meaning": (
            "AmoCRMdan endi kelgan, hali ishlanmagan lid. Darhol navbatga "
            "tushadi, lekin eng oxirgi o'rinda: avval berilgan va'dalar "
            "bajariladi, keyin yangilar olinadi."
        ),
        "in_queue": "Ha",
        "rank": "5",
        "keyword": "yangi",
    },
    {
        "status": "Uchrashuv vaqti",
        "ru": "Назначена встреча",
        "meaning": (
            "Uchrashuv boshqa kunga belgilangan, hozir qo'ng'iroq qilish "
            "shart emas. Uchrashuv kuni tizim uni o'zi \"Bugun keladi\" "
            "holatiga o'tkazadi."
        ),
        "in_queue": "Yo'q",
        "rank": "—",
        "keyword": "uchrashuv",
    },
    {
        "status": "Markazga keldi",
        "ru": "Пришёл в центр",
        "meaning": (
            "Mijoz markazga yetib kelgan — maqsad bajarilgan. Diqqat: "
            "\"Markazga kelmadi\" nomi ham shu turga tushadi, chunki tizim "
            "nomni so'z bo'lagi bo'yicha taniydi."
        ),
        "in_queue": "Yo'q",
        "rank": "—",
        "keyword": "markaz",
    },
    {
        "status": "Sifatsiz",
        "ru": "Некачественный лид",
        "meaning": (
            "4 urinishdan keyin ish to'xtatilgan lid. AI bu statusni tanlay "
            "olmaydi — uni faqat tizim qoidasi yoki odam qo'yadi. Boshqa "
            "navbatga qaytmaydi."
        ),
        "in_queue": "Yo'q",
        "rank": "—",
        "keyword": "sifatsiz",
    },
    {
        "status": "Boshqa (tanilmagan)",
        "ru": "Прочие (не распознан)",
        "meaning": (
            "Nomi tizimga tanish bo'lmagan har qanday status. Bunday lid "
            "hech qachon obzvonga tushmaydi va bu haqda hech qanday "
            "ogohlantirish chiqmaydi — statusni AmoCRMda qayta nomlashdan "
            "oldin shuni yodda tuting."
        ),
        "in_queue": "Yo'q",
        "rank": "—",
        "keyword": "—",
    },
)

STATUS_SHEET_NOTES_UZ: tuple[str, ...] = (
    "Tizim status nomini so'z bo'lagi bo'yicha taniydi: harflar kichik "
    "qilinadi, apostroflar olib tashlanadi (Ko'tarmadi = Kotarmadi).",
    "Nomlar yuqoridan pastga tekshiriladi va birinchi mos kelgani yutadi: "
    "\"Yangi lid — bugun keladi\" nomi \"Bugun keladi\" deb taniladi.",
    "Statuslar ro'yxati AmoCRMdagi har bir kompaniyaning o'z voronkasidan "
    "olinadi, shuning uchun nomlar turlicha bo'lishi mumkin.",
)

COLUMNS_UZ: tuple[str, ...] = (
    "№",
    "Kod",
    "Kim uchun (rol)",
    "Qayerda (ekran)",
    "Nima tekshirildi",
    "Qanday bo'lishi kerak",
    "Natija",
    "Izoh",
    "Muhimligi",
    "Davomiyligi (soniya)",
)

ROLE_COLUMNS_UZ: tuple[str, ...] = (
    "Rol",
    "Ishlayapti",
    "Tekshirildi",
    "Tekshirilmadi",
    "Jami",
)

DEFECT_COLUMNS_UZ: tuple[str, ...] = (
    "Xatolik kodi",
    "To'xtatilgan tekshiruvlar soni",
    "Tekshiruv kodlari",
)

# Ключ — UAT-ID; значения читает нетехнический сотрудник, поэтому
# «ekran» отвечает на «где», «scenario» — на «что делали», «expected» — на
# «как должно быть».
SCENARIOS_UZ: dict[str, dict[str, str]] = {
    "UAT-SYS-001": {
        "screen": "Server holati",
        "scenario": "Server ishlayapti va so'rovga javob beradi",
        "expected": (
            "So'rovdan oldin ham, keyin ham server \"tayyorman\" deb javob "
            "beradi; tariflar ro'yxati xatosiz ochiladi."
        ),
    },
    "UAT-SYS-002": {
        "screen": "Admin panel — kirish sahifasi",
        "scenario": "Yangi yuklangan Admin panel to'liq ochiladi",
        "expected": (
            "Kirish formasi to'liq ko'rinadi, sahifada xatolik chiqmaydi, "
            "barcha kerakli fayllar yuklanadi."
        ),
    },
    "UAT-COM-001": {
        "screen": "Til almashtirgich va shaxsiy kabinet",
        "scenario": "Foydalanuvchi rus va o'zbek tilini almashtiradi",
        "expected": (
            "Menyu va sarlavhalar sahifani qayta yuklamasdan tarjima bo'ladi; "
            "tanlangan til qayta kirgandan keyin ham saqlanadi; foydalanuvchi "
            "ma'lumotlari o'zgarmaydi."
        ),
    },
    "UAT-COM-002": {
        "screen": "Hisob menyusi / parolni o'zgartirish",
        "scenario": "Foydalanuvchi parolini o'zgartiradi va yangi parol bilan kiradi",
        "expected": (
            "Parol tushunarli tasdiq bilan o'zgaradi; yangi parol bilan kirish "
            "mumkin; vaqtinchalik hisob boshqariladigan holatda qoladi."
        ),
    },
    "UAT-LND-001": {
        "screen": "Landing sahifa",
        "scenario": "Landing ochiladi, menyu ishlaydi va amaldagi tariflarni ko'rsatadi",
        "expected": (
            "Sahifa to'liq yuklanadi, havolalar mavjud bo'limlarga olib boradi, "
            "Demo formasi ochiq, tariflar dolzarb va to'g'ri tartibda."
        ),
    },
    "UAT-LND-002": {
        "screen": "Demo arizasi → Super-admin lidlari",
        "scenario": "Demo arizasi Adminga yetib boradi va bitta ROP bo'lib ochiladi",
        "expected": (
            "Tashrifchi tasdiqni ko'radi, ariza bir marta tushadi, undan "
            "ma'lumotlari va tarifi to'g'ri bitta ROP yaratiladi."
        ),
    },
    "UAT-SA-001": {
        "screen": "Super-admin — kirish va menyu",
        "scenario": "Super-admin tizimga kiradi va o'z bo'limlarini ko'radi",
        "expected": (
            "Kirish muvaffaqiyatli; uchta asosiy bo'lim ma'lumotlari bilan "
            "xatosiz ochiladi; chiqish kirish formasiga qaytaradi."
        ),
    },
    "UAT-SA-002": {
        "screen": "ROPlar va kompaniya kartochkasi",
        "scenario": "Super-admin vaqtinchalik ROPni boshidan oxirigacha boshqaradi",
        "expected": (
            "Yaratish, tahrirlash, ichidagi operatorlarni ko'rish, o'chirib "
            "qo'yish, qayta yoqish va o'chirish nusxasiz bajariladi."
        ),
    },
    "UAT-SA-003": {
        "screen": "AmoCRM ulanishi",
        "scenario": "Ulangan AmoCRM o'z tuzilmasini qayta sinxronlaydi",
        "expected": (
            "Ulanish ishlayotgan ko'rinadi; qayta sinxronlash muvaffaqiyatli "
            "tugaydi va yangi tuzilma ROPga ko'rinadi."
        ),
    },
    "UAT-SA-004": {
        "screen": "OnlinePBX ulanishi",
        "scenario": "Ulangan OnlinePBX ichki raqamlar ro'yxatini qaytaradi",
        "expected": (
            "Integratsiya ulangan holatda ko'rinadi va faol ichki raqamlarni "
            "xatosiz qaytaradi."
        ),
    },
    "UAT-SA-005": {
        "screen": "Admin va Landing tariflari",
        "scenario": "Super-admin tarifni tahrirlaydi, Landing yangi qiymatni ko'rsatadi",
        "expected": (
            "O'zgarish Adminda ham, Landingda ham ko'rinadi; tarif kodi va "
            "boshqa tariflar o'zgarmaydi; dastlabki qiymatlar qaytariladi."
        ),
    },
    "UAT-SA-006": {
        "screen": "ROP yaratish va tarif imkoniyatlari",
        "scenario": "Super-admin har bir faol tarif bilan bittadan ROP yaratadi",
        "expected": (
            "Uchala faol tarif tanlash uchun ochiq; tizim to'g'ri tarifni "
            "qabul qiladi va har bir variant uchun aniq bitta ROP yaratadi."
        ),
    },
    "UAT-ROP-001": {
        "screen": "ROP — kirish va menyu",
        "scenario": "ROP tizimga kiradi va boshqaruv bo'limlarini ochadi",
        "expected": (
            "Kirish muvaffaqiyatli; har bir bo'lim o'z kompaniyasi ma'lumotlari "
            "bilan xatosiz yuklanadi."
        ),
    },
    "UAT-ROP-002": {
        "screen": "Operatorlar ro'yxati",
        "scenario": "ROP vaqtinchalik Operatorni boshidan oxirigacha boshqaradi",
        "expected": (
            "Yaratish, kirish, tahrirlash, parolni tiklash, o'chirib qo'yish, "
            "qayta yoqish, ko'rish va o'chirish bitta yozuvda ishlaydi."
        ),
    },
    "UAT-ROP-003": {
        "screen": "Navbat sozlamalari",
        "scenario": "ROP Operatorga voronkalarni biriktiradi va avvalgi holatga qaytaradi",
        "expected": (
            "Biriktirishlar nusxasiz saqlanadi; tanlangan Operator faqat "
            "belgilangan voronkalarni oladi."
        ),
    },
    "UAT-ROP-004": {
        "screen": "Qoidalar va kompaniya tavsifi",
        "scenario": "ROP AmoCRM tuzilmasini ko'radi va izohlarni saqlaydi",
        "expected": (
            "Ekran dolzarb tuzilmani ko'rsatadi; har bir o'zgarish kerakli "
            "joyga saqlanadi va boshqa voronkaga tegmaydi."
        ),
    },
    "UAT-ROP-005": {
        "screen": "Navbat mezonlari",
        "scenario": "ROP navbatning barcha ishchi mezonlarini saqlaydi",
        "expected": (
            "Sakkizala mezon saqlanadi va sahifa yangilangach o'rni "
            "almashmasdan, yaxlitlanmasdan ko'rinadi."
        ),
    },
    "UAT-ROP-006": {
        "screen": "Davomat",
        "scenario": "ROP Operatorining onlayn holati va smena yakunini ko'radi",
        "expected": (
            "ROP to'g'ri Operatorni, uning holatini va mos smena yakunlarini "
            "ko'radi; haftalar bo'ylab o'tish jadvalni buzmaydi."
        ),
    },
    "UAT-ROP-007": {
        "screen": "Operator kartochkasi",
        "scenario": "Operator kartochkasi dolzarb ma'lumot va voronkani ko'rsatadi",
        "expected": (
            "Kartochka tanlangan Operatorga tegishli va saqlangan voronkani "
            "sahifa yangilangach ham ko'rsatadi."
        ),
    },
    "UAT-ROP-008": {
        "screen": "Operator kartochkasi / qo'ng'iroqlar tarixi",
        "scenario": "ROP qo'ng'iroqni ochadi, yozuvni tinglaydi va matnini o'qiydi",
        "expected": (
            "Tarix yozuvlarni yashirmaydi; tanlangan qo'ng'iroq ma'lumotlari "
            "bilan ochiladi, audio eshitiladi, suhbat matni mavjud."
        ),
    },
    "UAT-OP-001": {
        "screen": "Operator — kirish, bosh sahifa va menyu",
        "scenario": "Operator tizimga kiradi va asosiy bo'limlarini ochadi",
        "expected": (
            "Kirish muvaffaqiyatli; to'rtta ish bo'limi xatosiz ochiladi, "
            "boshqa foydalanuvchi ma'lumoti bilan aralashmaydi."
        ),
    },
    "UAT-OP-002": {
        "screen": "Ish vaqti",
        "scenario": "Operator odatdagi ish kunini smena va tanaffus bilan o'tkazadi",
        "expected": (
            "Smena va tanaffus holatni ketma-ket o'zgartiradi; tugagach yakun "
            "o'smaydi va sahifa yangilangach saqlanib qoladi."
        ),
    },
    "UAT-OP-003": {
        "screen": "Ish vaqti / tanaffus tarixi",
        "scenario": "Tugagan tanaffus o'z davomiyligini ko'rsatadi",
        "expected": (
            "Qatorda tanaffusning boshlanishi, tugashi va hisoblangan "
            "davomiyligi ko'rinadi."
        ),
    },
    "UAT-OP-004": {
        "screen": "Qo'ng'iroq rejimi / navbat",
        "scenario": "Operator navbatni ko'radi va keyingi lidni ko'rsatma bilan oladi",
        "expected": (
            "Hisoblagich tayyorlangan lidni hisobga oladi; aynan o'sha lid "
            "beriladi; ko'rsatma va forma dolzarb ma'lumotni ko'rsatadi."
        ),
    },
    "UAT-OP-005": {
        "screen": "Qo'ng'iroqdan oldingi ko'rsatma",
        "scenario": "Operator taymerni boshqaradi va qo'ng'iroqni hoziroq boshlaydi",
        "expected": (
            "Pauza va davom ettirish taymerni boshqaradi; qo'lda boshlash "
            "xatosiz aniq bitta qo'ng'iroqni boshlaydi."
        ),
    },
    "UAT-OP-006": {
        "screen": "Qo'ng'iroqning to'liq aylanishi",
        "scenario": "Qo'ng'iroq liddan AI natijasigacha o'tadi va AmoCRMni yangilaydi",
        "expected": (
            "Qo'ng'iroq yozib olinadi va tahlil qilinadi; AI suhbatda "
            "tasdiqlangan ma'lumotni to'ldiradi, qo'lda kiritilgan ma'lumot "
            "ustun turadi, dastlabki lid nusxasiz yangilanadi."
        ),
    },
    "UAT-OP-007": {
        "screen": "Natijani tasdiqlash",
        "scenario": "Tayyor AI natijasi 20 soniyadan keyin o'zi sinxronlanadi",
        "expected": (
            "Taymer tugagach natija o'sha AmoCRM lidiga bir marta yuboriladi; "
            "interfeys qotib qolmaydi va nusxa yaratmaydi."
        ),
    },
    "UAT-OP-008": {
        "screen": "Ko'rsatma / lidni o'tkazib yuborish",
        "scenario": "Operator bitta lidni o'tkazib yuboradi va boshqasiga o'tadi",
        "expected": (
            "Birinchi lid urinish hisoblanmasdan bo'shatiladi va keyinga "
            "qoldiriladi; Operator boshqa lidni oladi va ishni davom ettiradi."
        ),
    },
    "UAT-OP-009": {
        "screen": "Qo'ng'iroqlar va bitim kartochkasi",
        "scenario": "Operator qo'ng'iroqlar ro'yxati va bitim tafsilotlarini ochadi",
        "expected": (
            "Ro'yxat tanlangan bitim ma'lumotini ko'rsatadi; o'tishlar bog'liq "
            "tafsilotlarni ochadi va ro'yxatni yo'qotmasdan ortga qaytaradi."
        ),
    },
    "UAT-OP-010": {
        "screen": "Qo'ng'iroqlar / jonli yangilanish",
        "scenario": "Yangi qo'ng'iroq ro'yxatda sahifani yangilamasdan paydo bo'ladi",
        "expected": (
            "Yangi qator jonli yangilanish orqali chiqadi va to'g'ri "
            "qo'ng'iroq sifatida ochiladi."
        ),
    },
    "UAT-FLOW-001": {
        "screen": "Obzvon navbati",
        "scenario": "Navbat beshta turdagi lidni to'g'ri tartibda beradi",
        "expected": (
            "Navbat lidlarni Bugun → Keyingi → Chala → Ko'tarmadi → Yangi "
            "tartibida beradi va har bir qo'ng'iroq sababini to'g'ri ko'rsatadi."
        ),
    },
    "UAT-FLOW-002": {
        "screen": "Uchrashuv statusi va qo'ng'iroq sababi",
        "scenario": "Vaqti kelgan uchrashuv lidni Bugun holatiga o'tkazadi",
        "expected": (
            "Lid \"Bugun keladi\" bo'ladi, kerakli paytda navbatga tushadi va "
            "qo'ng'iroq sababini bo'sh qiymatsiz, tushunarli ko'rsatadi."
        ),
    },
    "UAT-FLOW-003": {
        "screen": "To'rtinchi urinish va AmoCRM",
        "scenario": "To'rtinchi urinishdan keyin lid Sifatsiz bo'lib navbatdan chiqadi",
        "expected": (
            "Lidda aniq to'rtta urinish bor, status Sifatsiz bo'ldi, lid "
            "boshqa navbatga berilmaydi; AmoCRMga soxta ma'lumot ketmaydi."
        ),
    },
}


def role_uz(role: str) -> str:
    return ROLES_UZ.get(role, role)


def state_uz(state: str) -> str:
    return STATE_UZ.get(state, state)


def state_with_icon(state: str) -> str:
    icon = STATE_ICON.get(state, "")
    label = state_uz(state)
    return f"{icon} {label}".strip()


def priority_uz(priority: str) -> str:
    return PRIORITY_UZ.get(priority, priority)


def case_uz(case_id: str) -> dict[str, str]:
    """Узбекские тексты кейса; при отсутствии перевода вызывающий код
    обязан подставить русский оригинал, а не показывать пустую ячейку."""
    return SCENARIOS_UZ.get(case_id, {})


def human_datetime(iso_value: str) -> str:
    """ISO-строку показываем как «03.08.2026, soat 16:31» — техническая
    запись с «T» и смещением зоны нетехническому читателю мешает."""
    try:
        date_part, time_part = iso_value.split("T", 1)
        year, month, day = date_part.split("-")
        hour, minute = time_part.split(":")[:2]
    except ValueError:
        return iso_value
    return f"{day}.{month}.{year}, soat {hour}:{minute}"


def duration_uz(seconds: float) -> str:
    total = max(0, round(seconds))
    minutes, rest = divmod(total, 60)
    return f"{minutes} daqiqa {rest:02d} soniya"


def missing_translations(case_ids: tuple[str, ...] | list[str]) -> list[str]:
    """UAT-ID без перевода: используется тестом, чтобы новый сценарий
    не попал в узбекский отчёт с русским текстом незаметно."""
    return [case_id for case_id in case_ids if case_id not in SCENARIOS_UZ]
