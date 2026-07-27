# Адаптация Junior QA

[← Главная QA Wiki](../README.md) · [Далее: продукт и термины →](01-product-and-terms.md)

**Цель:** за пять рабочих дней научиться безопасно выполнять понятные
тест-кейсы и оформлять результат так, чтобы его мог проверить другой QA.

## Что Junior не обязан знать в первый день

Не нужно сразу понимать Go, React, SQL, устройство Gemini или все методы API.
Сначала нужно научиться:

- объяснять назначение продукта двумя предложениями;
- различать Super-admin, ROP и Operator;
- не путать staging и production;
- выполнять шаги тест-кейса без догадок;
- отличать `Failed` от `Blocked`;
- собирать доказательства и не раскрывать секреты;
- вовремя задавать вопрос.

## План первых пяти дней

### День 1 — продукт и безопасность

1. Прочитай [«Продукт и термины»](01-product-and-terms.md).
2. Открой две актуальные диаграммы и объясни наставнику их цвета.
3. Прочитай [правила окружений](02-environments-and-access.md).
4. Получи доступы по чек-листу, но не копируй логины и токены в Wiki.
5. Войди на staging под каждой доступной ролью и ничего не изменяй.

**Результат дня:** можешь показать, где staging, назвать три роли и объяснить,
почему функциональный тест на production запрещён.

### День 2 — лид и звонок

1. Прочитай разделы 1–3
   [глоссария статусов](../02-lead-status-glossary.md).
2. Пройди общую схему в [пути одного звонка](../04-call-flow.md).
3. На тестовом примере найди лида, его воронку, статус и число попыток.
4. Объясни путь: Operator AI → OnlinePBX → AI → AmoCRM.

**Результат дня:** понимаешь, почему лид может не попасть в очередь и где
искать сбой, если после разговора нет результата AI.

### День 3 — ручные кейсы

1. Прочитай [инструкцию по ручному прогону](04-manual-testing.md).
2. Под наблюдением выполни безопасный стартовый набор:
   TC-001–TC-005, TC-009, TC-021–TC-023.
3. Для каждого кейса заполни статус и комментарий с доказательством.
4. Попроси наставника проверить не результат продукта, а качество записей.

**Результат дня:** другой QA может повторить твою проверку только по записи
в Excel.

### День 4 — баги и диагностика

1. Прочитай [«Баги и вопросы»](05-defects-and-questions.md).
2. Возьми один учебный дефект или ранее закрытый баг.
3. Повтори его на staging, собери Network/Console и оформи черновик.
4. Сравни черновик с [шаблоном баг-репорта](../05-bugs.md#шаблон-копировать-отсюда).

**Результат дня:** умеешь оформить воспроизводимый дефект и не называешь
багом ситуацию с неизвестным ожидаемым результатом.

### День 5 — самостоятельный мини-регресс

1. Согласуй с наставником один небольшой модуль.
2. Проверь preflight окружения.
3. Выполни кейсы, зарегистрируй отклонения, перепроверь результаты.
4. Составь короткий отчёт по шаблону из
   [релизной страницы](06-release-and-reporting.md).
5. Проведи 15-минутный разбор: что было непонятно и чего не хватает в Wiki.

**Результат дня:** готов самостоятельно тестировать ограниченный модуль под
ревью более опытного QA.

## Чек-лист необходимых доступов

Фактические адреса и секреты выдаются через защищённое хранилище команды.

- [ ] staging Admin;
- [ ] staging Landing;
- [ ] адрес staging API;
- [ ] аккаунт Super-admin;
- [ ] аккаунт ROP тестовой компании;
- [ ] аккаунт Operator с тестовым внутренним номером;
- [ ] тестовая AmoCRM;
- [ ] тестовая OnlinePBX и разрешённые номера;
- [ ] API-документация `/docs` или `/openapi.yaml`;
- [ ] безопасный просмотр журналов staging;
- [ ] место регистрации задач и багов;
- [ ] папка для скриншотов/видео без публичного доступа.

Отсутствующий доступ отмечается как внешний блокер. Его нельзя заменять
production-аккаунтом или чужими учётными данными.

## Когда Junior работает самостоятельно

Можно работать самостоятельно, если одновременно:

- тест выполняется на staging;
- шаги и ожидаемый результат однозначны;
- используются подготовленные тестовые данные;
- действие обратимо и не затрагивает внешнего клиента;
- не требуется нагрузка, изменение конфигурации или выключение сервиса.

Во всех остальных случаях сначала согласуй действие.

## Ответственность внутри QA-команды

Фактическое назначение задач определяет команда, но базовое разделение такое:

| Уровень | За что отвечает |
| --- | --- |
| Junior QA | Выполняет подготовленные кейсы, собирает доказательства, создаёт черновики багов, сообщает о блокерах |
| Middle/Senior QA | Проектирует проверки сложных модулей, исследует интеграции и гонки, проводит triage, ревьюит результаты |
| QA Lead / ответственный за релиз | Управляет рисками и покрытием, согласует стратегию, принимает QA-решение GO/NO-GO |

Junior не должен молча принимать продуктовое решение или разрешать выпуск с
риском. Его ответственность — точно собрать факты и вовремя поднять вопрос.

## Короткий ежедневный статус

Используй один и тот же формат:

```text
Проверил:
Passed / Failed / Blocked:
Новые BUG/Q:
Что мешает:
Что проверю дальше:
Нужна помощь:
```

Возможную утечку, P0/P1 или действие на production сообщай сразу, не жди
ежедневного статуса.

## Проверка готовности

Junior готов к самостоятельному модулю, если может без подсказки:

- назвать источники правды в правильном порядке;
- показать разницу между `Failed`, `Blocked` и `Not Run`;
- объяснить, что `Passed` ставится только при полном совпадении результата;
- составить баг с шагами, ожиданием, фактом и доказательством;
- скрыть токен и персональные данные на скриншоте;
- назвать минимум две причины, почему лид не попадает в очередь;
- объяснить, почему 100% Passed не является математической гарантией
  отсутствия всех неизвестных дефектов.

---

## O‘zbekcha versiya

[← Asosiy QA Wiki](../README.md) · [Keyingi: mahsulot va atamalar →](01-product-and-terms.md)

**Maqsad:** besh ish kuni ichida tushunarli test-keyslarni xavfsiz bajarish va
natijani boshqa QA tekshira oladigan shaklda rasmiylashtirishni o‘rganish.

### Junior birinchi kuni nimalarni bilishi shart emas

Darhol Go, React, SQL, Gemini tuzilishi yoki barcha API metodlarini tushunish
shart emas. Avval quyidagilarni o‘rganish kerak:

- mahsulot vazifasini ikki gap bilan tushuntirish;
- Super-admin, ROP va Operator rollarini farqlash;
- staging va production’ni adashtirmaslik;
- test-keys qadamlarini taxminsiz bajarish;
- `Failed` va `Blocked` farqini bilish;
- dalillarni yig‘ish va sirlarni oshkor qilmaslik;
- savolni o‘z vaqtida berish.

### Birinchi besh kun rejasi

#### 1-kun — mahsulot va xavfsizlik

1. [«Mahsulot va atamalar»](01-product-and-terms.md) sahifasini o‘qing.
2. Ikki amaldagi diagrammani ochib, ularning ranglarini mentorga tushuntiring.
3. [Muhitlar qoidalarini](02-environments-and-access.md) o‘qing.
4. Checklist bo‘yicha kirishlarni oling, lekin login va tokenlarni Wiki’ga
   ko‘chirmang.
5. Staging’ga mavjud har bir rol bilan kiring va hech narsani o‘zgartirmang.

**Kun natijasi:** staging qayerdaligini ko‘rsata olasiz, uchta rolni aytasiz
va nima uchun production’da funksional test taqiqlanganini tushuntirasiz.

#### 2-kun — lid va qo‘ng‘iroq

1. [Statuslar lug‘atining](../02-lead-status-glossary.md) 1–3-bo‘limlarini
   o‘qing.
2. [Bitta qo‘ng‘iroq yo‘lidagi](../04-call-flow.md) umumiy sxemani ko‘rib
   chiqing.
3. Test misolida lidni, uning voronkasini, statusini va urinishlar sonini
   toping.
4. Operator AI → OnlinePBX → AI → AmoCRM yo‘lini tushuntiring.

**Kun natijasi:** lid nima uchun navbatga tushmasligini va suhbatdan keyin AI
natijasi bo‘lmasa, nosozlikni qayerdan izlashni tushunasiz.

#### 3-kun — qo‘lda bajariladigan keyslar

1. [Qo‘lda test o‘tkazish yo‘riqnomasini](04-manual-testing.md) o‘qing.
2. Nazorat ostida xavfsiz boshlang‘ich to‘plamni bajaring:
   TC-001–TC-005, TC-009, TC-021–TC-023.
3. Har bir keys uchun status va dalilli izoh yozing.
4. Mentordan mahsulot natijasini emas, yozuvlar sifatini tekshirishni so‘rang.

**Kun natijasi:** boshqa QA faqat Excel’dagi yozuv orqali tekshiruvingizni
takrorlay oladi.

#### 4-kun — baglar va diagnostika

1. [«Baglar va savollar»](05-defects-and-questions.md) sahifasini o‘qing.
2. Bitta o‘quv nuqsoni yoki avval yopilgan bagni oling.
3. Uni staging’da takrorlang, Network/Console ma’lumotlarini yig‘ing va
   qoralama tayyorlang.
4. Qoralamani [bag-report shabloni](../05-bugs.md#шаблон-копировать-отсюда)
   bilan solishtiring.

**Kun natijasi:** qayta tekshirish mumkin bo‘lgan nuqsonni rasmiylashtira
olasiz va kutilgan natija noma’lum holatni bag deb atamaysiz.

#### 5-kun — mustaqil mini-regress

1. Mentor bilan bitta kichik modulni kelishib oling.
2. Muhit preflight tekshiruvini bajaring.
3. Keyslarni bajaring, og‘ishlarni ro‘yxatdan o‘tkazing va natijalarni qayta
   tekshiring.
4. [Reliz sahifasidagi](06-release-and-reporting.md) shablon bo‘yicha qisqa
   hisobot tuzing.
5. 15 daqiqalik tahlil o‘tkazing: nima tushunarsiz bo‘ldi va Wiki’da nima
   yetishmaydi.

**Kun natijasi:** tajribaliroq QA ko‘rib chiqishi ostida cheklangan modulni
mustaqil testlashga tayyorsiz.

### Zarur kirishlar checklisti

Haqiqiy manzillar va sirlar jamoaning himoyalangan saqlash joyi orqali
beriladi.

- [ ] staging Admin;
- [ ] staging Landing;
- [ ] staging API manzili;
- [ ] Super-admin akkaunti;
- [ ] test kompaniyasining ROP akkaunti;
- [ ] test ichki raqamiga ega Operator akkaunti;
- [ ] test AmoCRM;
- [ ] test OnlinePBX va ruxsat berilgan raqamlar;
- [ ] `/docs` yoki `/openapi.yaml` API hujjatlari;
- [ ] staging loglarini xavfsiz ko‘rish imkoniyati;
- [ ] vazifalar va baglarni ro‘yxatdan o‘tkazish joyi;
- [ ] ommaviy kirishsiz skrinshot/video papkasi.

Yetishmayotgan kirish tashqi bloklovchi sabab sifatida qayd etiladi. Uni
production akkaunti yoki boshqa birovning hisob ma’lumotlari bilan
almashtirish mumkin emas.

### Junior qachon mustaqil ishlaydi

Quyidagi shartlarning barchasi bajarilsa, mustaqil ishlash mumkin:

- test staging’da bajarilmoqda;
- qadamlar va kutilgan natija bir ma’noli;
- tayyorlangan test ma’lumotlari ishlatilmoqda;
- harakatni qaytarish mumkin va u tashqi mijozga ta’sir qilmaydi;
- yuklama, konfiguratsiyani o‘zgartirish yoki servisni o‘chirish talab
  qilinmaydi.

Boshqa barcha holatlarda avval harakatni kelishib oling.

### QA jamoasi ichidagi mas’uliyat

Vazifalarning aniq taqsimotini jamoa belgilaydi, ammo asosiy bo‘linish
quyidagicha:

| Daraja | Mas’uliyati |
| --- | --- |
| Junior QA | Tayyor keyslarni bajaradi, dalillar yig‘adi, bag qoralamalarini yaratadi, bloklovchi sabablar haqida xabar beradi |
| Middle/Senior QA | Murakkab modullar tekshiruvlarini loyihalaydi, integratsiyalar va race condition’larni o‘rganadi, triage o‘tkazadi, natijalarni ko‘rib chiqadi |
| QA Lead / reliz uchun mas’ul | Xatarlar va qamrovni boshqaradi, strategiyani kelishadi, QA’ning GO/NO-GO qarorini qabul qiladi |

Junior mahsulot qarorini indamay qabul qilmasligi yoki xatarli relizga ruxsat
bermasligi kerak. Uning mas’uliyati — faktlarni aniq yig‘ish va savolni o‘z
vaqtida ko‘tarish.

### Qisqa kundalik status

Har doim bir xil formatdan foydalaning:

```text
Tekshirildi:
Passed / Failed / Blocked:
Yangi BUG/Q:
Nima xalaqit bermoqda:
Keyin nimani tekshiraman:
Yordam kerak:
```

Ehtimoliy ma’lumot sizib chiqishi, P0/P1 yoki production’dagi harakat haqida
kundalik statusni kutmasdan darhol xabar bering.

### Tayyorlikni tekshirish

Junior quyidagilarni yordamsiz bajara olsa, mustaqil modulga tayyor:

- haqiqat manbalarini to‘g‘ri tartibda aytish;
- `Failed`, `Blocked` va `Not Run` farqini ko‘rsatish;
- `Passed` faqat natija to‘liq mos kelganda qo‘yilishini tushuntirish;
- qadamlar, kutilgan natija, fakt va dalil bilan bag tuzish;
- skrinshotda token va shaxsiy ma’lumotlarni yashirish;
- lid navbatga tushmasligining kamida ikkita sababini aytish;
- nima uchun 100% Passed barcha noma’lum nuqsonlar yo‘qligiga matematik
  kafolat bermasligini tushuntirish.
