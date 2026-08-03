# QA Wiki — Operator AI

**Для кого:** Junior QA, новый участник QA-команды, наставник  
**Владелец:** QA-команда; изменения бизнес-правил ревьюит ответственный QA  
**Последняя сверка:** 27.07.2026  
**Проверяемый срез кода:** back `fb705b2`, admin `a761e40`, landing `246941c`

Эта Wiki — точка входа в проект. Она объясняет, что читать, что делать и когда
обращаться за помощью. Подробные технические документы не дублируются:
Wiki даёт короткое объяснение и ссылку на источник.

## Быстрый старт за 15 минут

1. Запомни главное правило: **функциональные проверки выполняются только на
   staging/test**. На production разрешено только пассивное наблюдение без
   изменения данных.
2. Прочитай [план адаптации](wiki/00-onboarding.md).
3. Разберись, [что делает продукт и кто его пользователи](wiki/01-product-and-terms.md).
4. Проверь [доступы и готовность окружения](wiki/02-environments-and-access.md).
5. Не начинай прогон, пока не понимаешь, какие данные можно создавать и удалять:
   [правила тестовых данных](wiki/03-test-data.md).

Если от тебя уже ждут ручной прогон, после этих пяти пунктов открой
[инструкцию по тест-кейсам](wiki/04-manual-testing.md).

## Маршрут обучения

| Порядок | Страница | Что должно стать понятно |
| ---: | --- | --- |
| 1 | [Адаптация Junior QA](wiki/00-onboarding.md) | Что делать в первые пять дней и когда остановиться |
| 2 | [Продукт и термины](wiki/01-product-and-terms.md) | Роли, интеграции и путь одного звонка |
| 3 | [Окружения и доступы](wiki/02-environments-and-access.md) | Где разрешено тестировать и что проверить перед стартом |
| 4 | [Тестовые данные](wiki/03-test-data.md) | Как подготовить данные и не задеть клиента |
| 5 | [Ручное тестирование](wiki/04-manual-testing.md) | Как выполнить кейс и поставить правильный статус |
| 6 | [Баги и вопросы](wiki/05-defects-and-questions.md) | Чем баг отличается от неясного требования |
| 7 | [Релиз и отчёт](wiki/06-release-and-reporting.md) | Когда QA может рекомендовать выпуск |
| 8 | [Диагностика](wiki/07-diagnostics.md) | Где искать причину ошибки и какие доказательства собрать |
| 9 | [Поддержка Wiki](wiki/08-wiki-maintenance.md) | Как обновлять документацию без появления противоречий |

## Источники правды

Если документы говорят разное, используй следующий порядок:

1. **Текущий код** показывает, что реально реализовано.
2. [Актуальная карта скоупа](06-scope-status.md) показывает, где код совпадает
   или расходится с продуктовым решением.
3. Две актуальные диаграммы показывают требуемое поведение:
   [жизненный цикл лида](<../docs/lead life-cycle.png>) и
   [карта экранов](<../docs/Operator AI site map.png>).
4. Ответы команды фиксируются в [журнале вопросов](03-questions-for-team.md).
5. [Тест-кейсы](07-test-cases.xlsx) показывают, как именно проверить требование.

Синий цвет на диаграмме означает «заявлено как реализованное», но не заменяет
проверку кода и staging. Фиолетовый означает «утверждено, но ещё не
реализовано». Красный — старое отменённое правило.

## Подробные документы проекта

| Документ | Когда открывать |
| --- | --- |
| [Анализ проекта](01-project-analysis.md) | Нужна полная карта функций, экранов, моделей данных и рисков |
| [Глоссарий статусов](02-lead-status-glossary.md) | Лид не попал в очередь или непонятно название статуса |
| [Вопросы к команде](03-questions-for-team.md) | Ожидание не определено или источники расходятся |
| [Путь одного звонка](04-call-flow.md) | Звонок, запись, AI или отправка в AmoCRM сломались |
| [Журнал багов](05-bugs.md) | Нужно зарегистрировать или перепроверить дефект |
| [Карта скоупа](06-scope-status.md) | Нужно понять, готова ли функция сейчас |
| [400 тест-кейсов](07-test-cases.xlsx) | Ручной прогон и фиксация результата |
| [Покрытие и Release Gate](08-release-readiness.md) | Подготовка решения GO/NO-GO |
| [Автоматизированные тест-кейсы](10-automated-test-cases.md) | Быстро увидеть покрытые pytest кейсы и открыть их код |
| [Ручные тест-кейсы](11-manual-test-cases.md) | Увидеть, какие кейсы ещё требуют ручной проверки |
| [Разведка ежедневного UAT](12-daily-uat-discovery.md) | Согласовать роли, основной путь, ресурсы и ограничения до отбора ежедневных сценариев |
| [Чеклист ежедневного happy-path UAT](13-daily-uat-checklist.md) | Согласовать минимальное позитивное покрытие всех активных функций до реализации |
| [Структурированный UAT-чеклист](daily-uat-checklist.json) | Машиночитаемые UAT-ID, шаги, ожидания, приоритеты, время, cleanup и блокеры |
| [Запуск и сопровождение ежедневного UAT](14-daily-uat-operations.md) | Runner, изолированные результаты, Telegram, расписание и правила красного дня |
| [Первый технический UAT-прогон 03.08.2026](15-daily-uat-run-2026-08-03.md) | Фактические 12/27, ресурсные ворота, дефектные блокеры и время 3:24 |
| [Первый стабильный GitHub UAT-прогон 03.08.2026](16-daily-uat-github-run-2026-08-03.md) | Расписание 08:00, серверный результат 12/27, Telegram-доставка и CI-адаптация |
| [Расширение ежедневного UAT 03.08.2026](17-daily-uat-expansion-run-2026-08-03.md) | Активация семи обработчиков, BUG-046 и стабильный результат 18/18 |
| [Полный ежедневный UAT 03.08.2026](18-daily-uat-full-run-2026-08-03.md) | Все 26 проверяемых сценариев, fixture cleanup, 5:54 и Telegram-доставка |

## Правила, при которых нужно остановиться

Не продолжай действие и обратись к ответственному QA, если:

- открыт production и следующий шаг изменяет данные;
- номер телефона не подтверждён как тестовый;
- в запросе, скриншоте или логе виден пароль, токен, ключ или данные клиента;
- ожидаемый результат противоречит коду, диаграмме или ответу команды;
- проверка может отправить реальный звонок, письмо или сообщение;
- требуется нагрузка, остановка сервиса или намеренное повреждение данных;
- обнаружена возможная утечка между компаниями или обход прав;
- непонятно, откатываются ли созданные данные.

Остановка в этих случаях — правильное действие QA, а не невыполненная работа.

---

## O‘zbekcha versiya

**Kimlar uchun:** Junior QA, QA jamoasining yangi a’zosi, mentor  
**Egasi:** QA jamoasi; biznes qoidalaridagi o‘zgarishlarni mas’ul QA ko‘rib chiqadi  
**Oxirgi tekshiruv:** 27.07.2026  
**Tekshirilayotgan kod kesimi:** back `fb705b2`, admin `a761e40`, landing `246941c`

Bu Wiki loyiha bilan tanishish uchun boshlang‘ich nuqtadir. U nimani o‘qish,
nima qilish va qachon yordam so‘rash kerakligini tushuntiradi. Batafsil texnik
hujjatlar bu yerda takrorlanmaydi: Wiki qisqa izoh va manbaga havola beradi.

### 15 daqiqada tezkor boshlash

1. Asosiy qoidani yodda tuting: **funksional tekshiruvlar faqat staging/test
   muhitida bajariladi**. Production muhitida ma’lumotlarni o‘zgartirmasdan
   faqat passiv kuzatishga ruxsat beriladi.
2. [Moslashuv rejasini](wiki/00-onboarding.md) o‘qing.
3. [Mahsulot nima qiladi va uning foydalanuvchilari kimligini](wiki/01-product-and-terms.md)
   tushunib oling.
4. [Kirish huquqlari va muhit tayyorligini](wiki/02-environments-and-access.md)
   tekshiring.
5. Qaysi ma’lumotlarni yaratish va o‘chirish mumkinligini tushunmaguningizcha
   testni boshlamang: [test ma’lumotlari qoidalari](wiki/03-test-data.md).

Agar sizdan qo‘lda test o‘tkazish kutilayotgan bo‘lsa, shu besh banddan keyin
[test-keyslardan foydalanish yo‘riqnomasini](wiki/04-manual-testing.md) oching.

### O‘rganish yo‘nalishi

| Tartib | Sahifa | Nima tushunarli bo‘lishi kerak |
| ---: | --- | --- |
| 1 | [Junior QA moslashuvi](wiki/00-onboarding.md) | Birinchi besh kunda nima qilish va qachon to‘xtash kerakligi |
| 2 | [Mahsulot va atamalar](wiki/01-product-and-terms.md) | Rollar, integratsiyalar va bitta qo‘ng‘iroq yo‘li |
| 3 | [Muhitlar va kirishlar](wiki/02-environments-and-access.md) | Qayerda test qilish mumkinligi va boshlashdan oldin nimani tekshirish kerakligi |
| 4 | [Test ma’lumotlari](wiki/03-test-data.md) | Ma’lumotlarni tayyorlash va mijozga zarar yetkazmaslik |
| 5 | [Qo‘lda testlash](wiki/04-manual-testing.md) | Keysni bajarish va to‘g‘ri status qo‘yish |
| 6 | [Baglar va savollar](wiki/05-defects-and-questions.md) | Bag noaniq talabdan nimasi bilan farq qilishi |
| 7 | [Reliz va hisobot](wiki/06-release-and-reporting.md) | QA qachon relizni tavsiya qilishi mumkinligi |
| 8 | [Diagnostika](wiki/07-diagnostics.md) | Xato sababini qayerdan izlash va qanday dalillarni yig‘ish |
| 9 | [Wiki’ni yuritish](wiki/08-wiki-maintenance.md) | Qarama-qarshiliklar paydo qilmasdan hujjatlarni yangilash |

### Haqiqat manbalari

Agar hujjatlarda turli ma’lumotlar bo‘lsa, quyidagi tartibdan foydalaning:

1. **Joriy kod** amalda nima implementatsiya qilinganini ko‘rsatadi.
2. [Amaldagi scope xaritasi](06-scope-status.md) kod mahsulot qaroriga qayerda
   mos kelishi yoki undan farq qilishini ko‘rsatadi.
3. Ikki amaldagi diagramma talab qilinadigan xatti-harakatni ko‘rsatadi:
   [lidning hayot sikli](<../docs/lead life-cycle.png>) va
   [ekranlar xaritasi](<../docs/Operator AI site map.png>).
4. Jamoa javoblari [savollar jurnalida](03-questions-for-team.md) qayd etiladi.
5. [Test-keyslar](07-test-cases.xlsx) talabni aynan qanday tekshirishni ko‘rsatadi.

Diagrammadagi ko‘k rang «implementatsiya qilingan deb ko‘rsatilgan» degan
ma’noni beradi, ammo kod va staging tekshiruvini almashtirmaydi. Binafsha rang
«tasdiqlangan, lekin hali implementatsiya qilinmagan» degani. Qizil rang —
bekor qilingan eski qoida.

### Loyihaning batafsil hujjatlari

| Hujjat | Qachon ochish kerak |
| --- | --- |
| [Loyiha tahlili](01-project-analysis.md) | Funksiyalar, ekranlar, ma’lumotlar modellari va xatarlarning to‘liq xaritasi kerak bo‘lsa |
| [Statuslar lug‘ati](02-lead-status-glossary.md) | Lid navbatga tushmasa yoki status nomi tushunarsiz bo‘lsa |
| [Jamoaga savollar](03-questions-for-team.md) | Kutilgan natija aniqlanmagan yoki manbalar bir-biriga zid bo‘lsa |
| [Bitta qo‘ng‘iroq yo‘li](04-call-flow.md) | Qo‘ng‘iroq, yozuv, AI yoki AmoCRM’ga yuborish ishlamasa |
| [Baglar jurnali](05-bugs.md) | Nuqsonni ro‘yxatdan o‘tkazish yoki qayta tekshirish kerak bo‘lsa |
| [Scope xaritasi](06-scope-status.md) | Funksiya hozir tayyormi yoki yo‘qligini tushunish kerak bo‘lsa |
| [400 ta test-keys](07-test-cases.xlsx) | Qo‘lda test o‘tkazish va natijani qayd etish uchun |
| [Qamrov va Release Gate](08-release-readiness.md) | GO/NO-GO qarorini tayyorlash uchun |
| [Avtomatlashtirilgan test-keyslar](10-automated-test-cases.md) | Pytest bilan qamrab olingan keyslar va ularning kodini tez topish uchun |
| [Qo‘lda bajariladigan test-keyslar](11-manual-test-cases.md) | Hali qo‘lda tekshirilishi kerak bo‘lgan keyslarni ko‘rish uchun |
| [Kunlik UAT razvedkasi (ruscha)](12-daily-uat-discovery.md) | Kundalik ssenariylarni tanlashdan oldin rollar, asosiy yo‘l, resurslar va cheklovlarni kelishish uchun |
| [Kunlik happy-path UAT ro‘yxati (ruscha)](13-daily-uat-checklist.md) | Amalga oshirishdan oldin barcha faol funksiyalarning minimal ijobiy qamrovini kelishish uchun |
| [Tuzilgan UAT ro‘yxati](daily-uat-checklist.json) | UAT-ID, qadamlar, kutilgan natijalar, ustuvorliklar, vaqt, cleanup va bloklovchilar |
| [Kunlik UAT’ni ishga tushirish va kuzatish (ruscha)](14-daily-uat-operations.md) | Runner, alohida natijalar, Telegram, jadval va qizil kun qoidalari |
| [03.08.2026 texnik UAT natijasi (ruscha)](15-daily-uat-run-2026-08-03.md) | Haqiqiy 12/27 natija, resurs to‘siqlari, defect bloklari va 3:24 vaqt |
| [03.08.2026 birinchi barqaror GitHub UAT natijasi (ruscha)](16-daily-uat-github-run-2026-08-03.md) | 08:00 jadvali, 12/27 server natijasi, Telegram yetkazib berish va CI moslashtirish |
| [03.08.2026 kunlik UAT kengaytmasi (ruscha)](17-daily-uat-expansion-run-2026-08-03.md) | Yetti yangi handler, BUG-046 va 18/18 barqaror natija |
| [03.08.2026 to‘liq kunlik UAT (ruscha)](18-daily-uat-full-run-2026-08-03.md) | Barcha 26 tekshiriladigan ssenariy, fixture cleanup, 5:54 va Telegram yetkazib berish |

### To‘xtash kerak bo‘lgan holatlar

Quyidagi holatlarda harakatni davom ettirmang va mas’ul QA’ga murojaat qiling:

- production ochiq bo‘lsa va keyingi qadam ma’lumotlarni o‘zgartirsa;
- telefon raqami test raqami sifatida tasdiqlanmagan bo‘lsa;
- so‘rov, skrinshot yoki logda parol, token, kalit yoki mijoz ma’lumotlari
  ko‘rinsa;
- kutilgan natija kod, diagramma yoki jamoa javobiga zid bo‘lsa;
- tekshiruv haqiqiy qo‘ng‘iroq, xat yoki xabar yuborishi mumkin bo‘lsa;
- yuklama, servisni to‘xtatish yoki ma’lumotlarni ataylab buzish talab qilinsa;
- kompaniyalar orasida ehtimoliy ma’lumot sizib chiqishi yoki huquqlarni
  chetlab o‘tish aniqlansa;
- yaratilgan ma’lumotlar qanday qaytarilishi noma’lum bo‘lsa.

Bunday holatlarda to‘xtash — bajarilmagan ish emas, balki QA’ning to‘g‘ri
harakatidir.
