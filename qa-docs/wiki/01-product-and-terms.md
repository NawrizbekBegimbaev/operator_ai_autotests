# Продукт и термины

[← Адаптация](00-onboarding.md) · [Главная](../README.md) ·
[Далее: окружения →](02-environments-and-access.md)

## Operator AI за две минуты

Operator AI — помощник отдела продаж между оператором и AmoCRM. Он выбирает
следующего клиента для звонка, получает запись разговора из OnlinePBX,
расшифровывает её с помощью AI и предлагает оператору статус и значения полей.
Оператор проверяет предложение, подтверждает его, после чего результат
синхронизируется в AmoCRM.

Бытовая аналогия: это диспетчер, секретарь и контролёр качества в одном
продукте. Диспетчер выбирает, кому звонить; секретарь делает конспект;
контролёр просит человека подтвердить результат перед записью в CRM.

Operator AI **не заменяет AmoCRM**. Источником клиентских лидов, воронок,
статусов и части полей остаётся AmoCRM.

## Три роли

| Роль | Кто это | Основная работа | Чего не должен видеть |
| --- | --- | --- | --- |
| Super-admin | Сотрудник владельца Operator AI | Создаёт клиентов-ROP, подключает интеграции, управляет тарифами | Рабочие данные чужого клиента без разрешённого сценария |
| ROP | Руководитель отдела продаж клиента | Создаёт операторов, настраивает воронки, очередь, поля и смотрит отчёты | Данные другой компании и функции Super-admin |
| Operator | Менеджер по звонкам | Ведёт смену, получает лидов, звонит и подтверждает результат | Настройки ROP, тарифы, пользователи и чужая компания |

В архитектуре ROP одновременно представляет компанию. Поэтому проверка
«компания А не видит компанию Б» обязательна почти для каждого API и экрана.

Полная карта экранов находится в
[актуальной диаграмме](<../../docs/Operator AI site map.png>) и в
[анализе проекта](../01-project-analysis.md#4-карта-экранов-сайт-мап-по-коду).

## Из чего состоит система

| Компонент | Простое объяснение | Что проверяет QA |
| --- | --- | --- |
| Admin | Веб-интерфейс трёх ролей | Экраны, формы, навигацию, права, ошибки |
| Backend | Правила и API продукта | Данные, права, очередь, идемпотентность, интеграции |
| Landing | Публичный сайт и demo-заявка | Форму, валидацию, безопасность, передачу заявки |
| PostgreSQL | Основное хранилище | Целостность через UI/API; прямые изменения QA запрещены |
| AmoCRM | CRM клиента | Лиды, воронки, статусы, поля и итог синхронизации |
| OnlinePBX | Телефония | Набор, событие звонка, запись и внутренний номер |
| Gemini | AI-провайдер | Транскрипцию и предложение полей; окончательное решение подтверждает человек |

Код находится в трёх каталогах `project/back`, `project/admin` и
`project/landing`. Для QA этот каталог только для чтения.

## Путь одного звонка

1. Operator начинает смену и открывает режим обзвона.
2. Backend выбирает самого срочного доступного лида и временно блокирует его.
3. Admin показывает причину звонка и запускает предзвон.
4. OnlinePBX соединяет оператора с тестовым клиентом и создаёт запись.
5. Backend получает вебхук или находит звонок фоновым опросом.
6. AI расшифровывает запись и предлагает статус и значения полей.
7. Operator проверяет результат. Изменение человеком важнее предложения AI.
8. После подтверждения Backend обновляет исходный лид в AmoCRM.
9. Система выдаёт следующего лида.

Подробная схема, таймеры и точки отказа:
[«Путь одного звонка»](../04-call-flow.md).

## Основные бизнес-правила

- Очередь общая: лид не принадлежит одному оператору навсегда.
- Два оператора не должны одновременно получить одного лида.
- Приоритет очереди: `Bugun` → `Keyingi` → `Chala` → `Ko'tarmadi` → `Yangi`.
- Общий лимит — четыре попытки, а не четыре попытки каждый день.
- Неиспользованные попытки переносятся на следующие рабочие дни.
- Сам недозвон не разрешает автоматически записать `Ko'tarmadi` в AmoCRM.
- После 4/4 система переводит лид в `Sifatsiz`, отправляет изменение в AmoCRM
  и больше не выдаёт его.
- `Yangi` и `Sifatsiz` не выбираются AI как обычный исход разговора.
- Поле Operator заполняется вошедшим пользователем, а не угадывается из аудио.
- Админка работает на узбекском и русском, но названия статусов в MVP
  остаются узбекскими.

Перед проверкой жизненного цикла обязательно открой
[актуальную карту скоупа](../06-scope-status.md), потому что часть новых правил
ещё отложена.

## Мини-глоссарий

| Термин | Простое значение |
| --- | --- |
| Лид | Потенциальный клиент или сделка, которой нужно заняться |
| Воронка / pipeline | Набор этапов продажи в AmoCRM |
| Статус | Текущий этап лида внутри конкретной воронки |
| Tenant / компания | Изолированная область одного клиента Operator AI |
| RBAC | Правила, определяющие, что разрешено каждой роли |
| API | Способ, которым интерфейс и внешние системы обращаются к Backend |
| Webhook | Уведомление от внешней системы о событии |
| WebRTC | Звонок из браузера |
| Click-to-call | Команда серверу/телефонии начать звонок |
| Транскрипция | Текст, полученный из записи разговора |
| Human-in-the-loop | AI предлагает, но человек проверяет и подтверждает |
| Идемпотентность | Повтор одного события не создаёт вторую запись |
| Smoke | Короткая проверка, что основные части версии вообще запускаются |
| Регресс | Проверка, что изменение не сломало ранее работавшие функции |

## Статусы лида, которые нужно узнавать

| Узбекское название | Русский смысл | Общая роль в очереди |
| --- | --- | --- |
| `Bugun keladi` | Придёт сегодня | Самый высокий приоритет |
| `Keyingi qo'ng'iroq vaqti` | Время следующего звонка | Выдаётся в назначенное время |
| `Chala gaplashdi` | Разговор не завершён | Нужен повторный контакт |
| `Ko'tarmadi` | Не поднял трубку | Повтор после недозвона |
| `Yangi lid` | Новый лид | Обычный новый контакт |
| `Uchrashuv` | Встреча назначена | До нужного времени вне обычной очереди |
| `Markazga keldi` | Пришёл в центр | Вне обзвона |
| `Sifatsiz` | Некачественный лид | Финал после исчерпания попыток |

Названия у разных клиентов могут отличаться. Система распознаёт их по
ключевым словам, поэтому полные правила и опасные совпадения смотри в
[глоссарии статусов](../02-lead-status-glossary.md).

---

## O‘zbekcha versiya

[← Moslashuv](00-onboarding.md) · [Asosiy sahifa](../README.md) ·
[Keyingi: muhitlar →](02-environments-and-access.md)

### Operator AI ikki daqiqada

Operator AI — operator va AmoCRM o‘rtasida ishlaydigan savdo bo‘limi
yordamchisi. U qo‘ng‘iroq qilish uchun keyingi mijozni tanlaydi, OnlinePBX’dan
suhbat yozuvini oladi, AI yordamida uni matnga aylantiradi hamda operatorga
status va maydon qiymatlarini taklif qiladi. Operator taklifni tekshirib,
tasdiqlaydi, shundan keyin natija AmoCRM bilan sinxronlanadi.

Oddiy o‘xshatish: bu bitta mahsulot ichidagi dispetcher, kotib va sifat
nazoratchisi. Dispetcher kimga qo‘ng‘iroq qilishni tanlaydi, kotib suhbatni
qisqacha yozadi, nazoratchi esa CRM’ga yozishdan oldin insondan natijani
tasdiqlashni so‘raydi.

Operator AI **AmoCRM o‘rnini bosmaydi**. Mijoz lidlari, voronkalar, statuslar
va ayrim maydonlarning manbasi AmoCRM bo‘lib qoladi.

### Uchta rol

| Rol | Bu kim | Asosiy ishi | Nimalarni ko‘rmasligi kerak |
| --- | --- | --- | --- |
| Super-admin | Operator AI egasi tomondagi xodim | ROP mijozlarini yaratadi, integratsiyalarni ulaydi, tariflarni boshqaradi | Ruxsat berilgan ssenariysiz boshqa mijozning ish ma’lumotlarini |
| ROP | Mijozning savdo bo‘limi rahbari | Operatorlar yaratadi, voronka, navbat va maydonlarni sozlaydi, hisobotlarni ko‘radi | Boshqa kompaniya ma’lumotlari va Super-admin funksiyalarini |
| Operator | Qo‘ng‘iroqlar bilan ishlovchi menejer | Smenani olib boradi, lidlarni oladi, qo‘ng‘iroq qiladi va natijani tasdiqlaydi | ROP sozlamalari, tariflar, foydalanuvchilar va boshqa kompaniyani |

Arxitekturada ROP bir vaqtning o‘zida kompaniyani ham ifodalaydi. Shu sababli
«A kompaniya B kompaniyani ko‘rmaydi» tekshiruvi deyarli har bir API va ekran
uchun majburiy.

Ekranlarning to‘liq xaritasi [amaldagi diagrammada](<../../docs/Operator AI site map.png>)
va [loyiha tahlilida](../01-project-analysis.md#4-карта-экранов-сайт-мап-по-коду)
joylashgan.

### Tizim nimalardan iborat

| Komponent | Oddiy tushuntirish | QA nimani tekshiradi |
| --- | --- | --- |
| Admin | Uch rol uchun veb-interfeys | Ekranlar, formalar, navigatsiya, huquqlar, xatolar |
| Backend | Mahsulot qoidalari va API | Ma’lumotlar, huquqlar, navbat, idempotentlik, integratsiyalar |
| Landing | Ommaviy sayt va demo ariza | Forma, validatsiya, xavfsizlik, arizani uzatish |
| PostgreSQL | Asosiy ma’lumotlar ombori | UI/API orqali yaxlitlik; QA’ga to‘g‘ridan-to‘g‘ri o‘zgartirish taqiqlangan |
| AmoCRM | Mijoz CRM’i | Lidlar, voronkalar, statuslar, maydonlar va yakuniy sinxronlash |
| OnlinePBX | Telefoniya | Raqam terish, qo‘ng‘iroq hodisasi, yozuv va ichki raqam |
| Gemini | AI provayder | Transkripsiya va maydonlar taklifi; yakuniy qarorni inson tasdiqlaydi |

Kod `project/back`, `project/admin` va `project/landing` kataloglarida
joylashgan. QA uchun bu katalog faqat o‘qish rejimida.

### Bitta qo‘ng‘iroq yo‘li

1. Operator smenani boshlaydi va qo‘ng‘iroq rejimini ochadi.
2. Backend eng shoshilinch mavjud lidni tanlaydi va uni vaqtincha bloklaydi.
3. Admin qo‘ng‘iroq sababini ko‘rsatadi va pre-call jarayonini boshlaydi.
4. OnlinePBX operatorni test mijoz bilan ulaydi va yozuv yaratadi.
5. Backend webhook oladi yoki fon so‘rovi orqali qo‘ng‘iroqni topadi.
6. AI yozuvni matnga aylantirib, status va maydon qiymatlarini taklif qiladi.
7. Operator natijani tekshiradi. Inson kiritgan o‘zgarish AI taklifidan ustun.
8. Tasdiqlangandan keyin Backend AmoCRM’dagi dastlabki lidni yangilaydi.
9. Tizim keyingi lidni beradi.

Batafsil sxema, taymerlar va nosozlik nuqtalari:
[«Bitta qo‘ng‘iroq yo‘li»](../04-call-flow.md).

### Asosiy biznes qoidalari

- Navbat umumiy: lid bitta operatorga abadiy tegishli bo‘lib qolmaydi.
- Ikki operator bir vaqtda bitta lidni olmasligi kerak.
- Navbat ustuvorligi: `Bugun` → `Keyingi` → `Chala` → `Ko'tarmadi` → `Yangi`.
- Umumiy limit — har kuni to‘rttadan emas, jami to‘rtta urinish.
- Ishlatilmagan urinishlar keyingi ish kunlariga o‘tadi.
- Javobsiz qo‘ng‘iroqning o‘zi AmoCRM’ga avtomatik `Ko'tarmadi` yozishga
  ruxsat bermaydi.
- 4/4 urinishdan keyin tizim lidni `Sifatsiz` statusiga o‘tkazadi, o‘zgarishni
  AmoCRM’ga yuboradi va uni boshqa bermaydi.
- `Yangi` va `Sifatsiz` AI tomonidan suhbatning oddiy natijasi sifatida
  tanlanmaydi.
- Operator maydoni audiodan taxmin qilinmaydi, tizimga kirgan foydalanuvchi
  bilan to‘ldiriladi.
- Admin panel o‘zbek va rus tillarida ishlaydi, ammo MVP’da status nomlari
  o‘zbekcha qoladi.

Hayot siklini tekshirishdan oldin [amaldagi scope xaritasini](../06-scope-status.md)
albatta oching, chunki yangi qoidalarning bir qismi hali kechiktirilgan.

### Qisqa lug‘at

| Atama | Oddiy ma’nosi |
| --- | --- |
| Lid | Ishlash kerak bo‘lgan potensial mijoz yoki bitim |
| Voronka / pipeline | AmoCRM’dagi savdo bosqichlari to‘plami |
| Status | Muayyan voronka ichidagi lidning joriy bosqichi |
| Tenant / kompaniya | Bitta Operator AI mijozining ajratilgan hududi |
| RBAC | Har bir rolga nima ruxsat etilganini belgilovchi qoidalar |
| API | Interfeys va tashqi tizimlarning Backend’ga murojaat qilish usuli |
| Webhook | Tashqi tizimning hodisa haqida xabari |
| WebRTC | Brauzer orqali qo‘ng‘iroq |
| Click-to-call | Server/telefoniyaga qo‘ng‘iroqni boshlash buyrug‘i |
| Transkripsiya | Suhbat yozuvidan olingan matn |
| Human-in-the-loop | AI taklif qiladi, inson esa tekshiradi va tasdiqlaydi |
| Idempotentlik | Bitta hodisaning takrori ikkinchi yozuvni yaratmaydi |
| Smoke | Versiyaning asosiy qismlari umuman ishga tushishini qisqa tekshirish |
| Regress | O‘zgarish avval ishlagan funksiyalarni buzmaganini tekshirish |

### Tanib olish kerak bo‘lgan lid statuslari

| O‘zbekcha nomi | Ruscha ma’nosi | Navbatdagi umumiy roli |
| --- | --- | --- |
| `Bugun keladi` | Придёт сегодня | Eng yuqori ustuvorlik |
| `Keyingi qo'ng'iroq vaqti` | Время следующего звонка | Belgilangan vaqtda beriladi |
| `Chala gaplashdi` | Разговор не завершён | Qayta aloqa kerak |
| `Ko'tarmadi` | Не поднял трубку | Javobsiz qo‘ng‘iroqdan keyin takror |
| `Yangi lid` | Новый лид | Oddiy yangi aloqa |
| `Uchrashuv` | Встреча назначена | Kerakli vaqtgacha oddiy navbatdan tashqarida |
| `Markazga keldi` | Пришёл в центр | Qo‘ng‘iroq navbatidan tashqarida |
| `Sifatsiz` | Некачественный лид | Urinishlar tugagandan keyingi yakun |

Turli mijozlarda nomlar farq qilishi mumkin. Tizim ularni kalit so‘zlar
bo‘yicha taniydi, shuning uchun to‘liq qoidalar va xavfli mosliklarni
[statuslar lug‘atida](../02-lead-status-glossary.md) ko‘ring.
