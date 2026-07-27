# Диагностика для QA

[← Релиз](06-release-and-reporting.md) · [Главная](../README.md) ·
[Далее: поддержка Wiki →](08-wiki-maintenance.md)

Цель диагностики QA — не обязательно найти строку с ошибкой в коде. Нужно
локализовать участок цепочки и собрать достаточно фактов, чтобы разработчик
воспроизвёл проблему.

## Минимальный набор инструментов

| Инструмент | Для чего |
| --- | --- |
| Browser DevTools — Network | Запрос, код ответа, время, payload |
| Browser DevTools — Console | Ошибки JavaScript и предупреждения |
| Application/Storage | Сессия и локальное состояние; не публиковать токены |
| `/docs` и `/openapi.yaml` | Актуальный контракт API |
| Postman/curl | Повтор запроса без UI |
| `/healthz`, `/readyz` | Жив ли Backend и готов ли обслуживать запросы |
| Логи staging | Correlation/request ID и причина серверной ошибки |
| Excel тест-кейсов | Ожидание и история выполнения |
| Скриншот/видео | Визуальное доказательство |

Прямое изменение базы данных не является обычным инструментом QA. Если
доступ на чтение выдан, используй его только для подтверждения; изменения
делай через продуктовый API или согласованный скрипт.

## Шпаргалка HTTP

| Код | Обычно означает | Что проверить |
| ---: | --- | --- |
| 200/201/204 | Успех | Тело, побочный эффект и отсутствие дубля |
| 400 | Некорректный запрос | Поля ошибки и понятность сообщения |
| 401 | Нет действующей аутентификации | Токен, refresh, cookie, выход |
| 403 | Пользователь известен, но действие запрещено | Роль и tenant |
| 404 | Ресурс не найден или безопасно скрыт | ID, компания и отсутствие утечки |
| 409 | Конфликт состояния или дубль | Идемпотентность и существующую запись |
| 422 | Семантически неверные данные | Контракт и ошибки полей |
| 429 | Слишком много запросов | Rate limit и время восстановления |
| 500 | Необработанная серверная ошибка | Request ID и лог |
| 502/503/504 | Сервис/зависимость недоступны | Health, deploy, внешнюю систему |

Успешный HTTP-код не доказывает успешный бизнес-результат. Всегда проверяй
сохранённые данные.

## Если не удаётся войти

1. Проверь staging URL и роль аккаунта.
2. Убедись, что аккаунт активен.
3. Проверь Network-запрос login и его код.
4. Сравни ошибку неверного пароля и несуществующего пользователя.
5. Убедись, что не сработал rate limit.
6. Проверь refresh/cookie только локально, не копируя значения.
7. Попробуй чистое приватное окно.
8. Зафиксируй, происходит ли ошибка в UI или уже в API.

## Если очередь показывает 0

Проверь по порядку:

1. Operator начал смену.
2. Operator назначен на нужную воронку.
3. Воронка выбрана и синхронизирована.
4. У лида есть тестовый телефон.
5. Статус распознаётся системой.
6. Время следующего звонка уже наступило.
7. Лид не находится вне рабочих часов.
8. Число попыток меньше четырёх.
9. Лид не финальный и не удалён.
10. Нет активной блокировки или незакрытой сессии.
11. Лид принадлежит правильной компании.

Расширенный чек-лист:
[«Почему лид может пропасть»](../02-lead-status-glossary.md#11-чек-лист-почему-лид-может-пропасть-из-обзвона).

## Если звонок не начинается

1. Проверь, используется WebRTC или click-to-call.
2. Проверь тестовый номер и направление звонка.
3. Убедись, что у Operator заполнен внутренний номер.
4. Проверь, что внутренний номер включён в OnlinePBX.
5. Проверь активность конфигурации OnlinePBX.
6. Найди исходящий запрос и ответ телефонии.
7. Проверь, создалась ли сессия звонка и не истекла ли блокировка.
8. Не повторяй звонок многократно, пока не уверен, что номер тестовый.

## Если нет записи или AI-результата

Раздели цепочку:

```text
Звонок завершён
  → событие OnlinePBX получено
  → запись доступна
  → аудио сохранено
  → транскрипция запущена
  → Gemini ответил
  → поля сохранены
  → UI получил результат
```

Проверь:

- был ли разговор отвеченным и есть ли `dialog_duration`;
- дошёл ли вебхук и не был ли он дублем;
- сработал ли страховочный опрос;
- доступна ли ссылка на запись;
- нет ли квоты/ошибки Gemini;
- не попал ли ключ в лог;
- не исчерпаны ли retry;
- соответствует ли ответ полям формы;
- не истёк ли клиентский таймер ожидания.

Подробные точки отказа:
[путь звонка, раздел 6](../04-call-flow.md#6-где-процесс-может-сломаться-карта-отказов).

## Если результат не появился в AmoCRM

1. Проверь, что Operator действительно подтвердил форму.
2. Зафиксируй один запрос отправки и его ответ.
3. Проверь активную конфигурацию AmoCRM.
4. Проверь правильную компанию и воронку.
5. Убедись, что обновляется исходный лид, а не создаётся новый.
6. Сравни pipeline/status ID.
7. Проверь поля группы `Operator AI`.
8. Убедись, что select отправляется корректным enum ID.
9. Проверь состояние лида непосредственно в тестовой AmoCRM.
10. Повтори чтение, но не повторяй изменяющий запрос без проверки
    идемпотентности.

## Если UI показывает старые или чужие данные

- проверь роль и tenant текущей сессии;
- проверь параметры запроса и фильтры;
- проверь cache TanStack Query после смены пользователя;
- проверь SSE-поток и его закрытие после logout;
- повтори в приватном окне;
- проверь кнопку Назад после выхода;
- сравни API-ответ и отображение;
- при чужих данных остановись и эскалируй как безопасность.

## Что приложить разработчику

Минимальный диагностический пакет:

```text
Время с часовым поясом:
Окружение и версия:
Роль и тестовая компания:
ID кейса:
ID сущности:
Последний успешный шаг:
Первый сломанный шаг:
Request method/path/status:
Request/correlation ID:
Безопасная часть response:
Console:
Повторяемость:
Скриншот/видео:
```

Не отправляй разработчику «посмотри логи» без времени, request ID и
описания действия.

---

## O‘zbekcha versiya

[← Reliz](06-release-and-reporting.md) · [Asosiy sahifa](../README.md) ·
[Keyingi: Wiki’ni yuritish →](08-wiki-maintenance.md)

QA diagnostikasining maqsadi koddagi xato qatorini albatta topish emas.
Zanjirning muammoli qismini ajratish va dasturchi muammoni takrorlay olishi
uchun yetarli faktlarni yig‘ish kerak.

### Minimal vositalar to‘plami

| Vosita | Nima uchun |
| --- | --- |
| Browser DevTools — Network | So‘rov, javob kodi, vaqt, payload |
| Browser DevTools — Console | JavaScript xatolari va ogohlantirishlari |
| Application/Storage | Sessiya va lokal holat; tokenlarni e’lon qilmaslik |
| `/docs` va `/openapi.yaml` | Amaldagi API shartnomasi |
| Postman/curl | So‘rovni UI’siz takrorlash |
| `/healthz`, `/readyz` | Backend ishlayaptimi va so‘rovlarga tayyormi |
| Staging loglari | Correlation/request ID va server xatosi sababi |
| Test-keyslar Excel’i | Kutilgan natija va bajarish tarixi |
| Skrinshot/video | Vizual dalil |

Ma’lumotlar bazasini to‘g‘ridan-to‘g‘ri o‘zgartirish QA’ning odatiy vositasi
emas. O‘qish huquqi berilgan bo‘lsa, undan faqat tasdiqlash uchun foydalaning;
o‘zgarishlarni mahsulot API’si yoki kelishilgan skript orqali bajaring.

### HTTP bo‘yicha qisqa qo‘llanma

| Kod | Odatda nimani anglatadi | Nimani tekshirish kerak |
| ---: | --- | --- |
| 200/201/204 | Muvaffaqiyat | Body, yon ta’sir va dubl yo‘qligi |
| 400 | Noto‘g‘ri so‘rov | Xato maydonlari va xabarning tushunarliligi |
| 401 | Amaldagi autentifikatsiya yo‘q | Token, refresh, cookie, logout |
| 403 | Foydalanuvchi ma’lum, ammo harakat taqiqlangan | Rol va tenant |
| 404 | Resurs topilmadi yoki xavfsiz yashirildi | ID, kompaniya va sizib chiqish yo‘qligi |
| 409 | Holat konflikti yoki dubl | Idempotentlik va mavjud yozuv |
| 422 | Semantik jihatdan noto‘g‘ri ma’lumot | Shartnoma va maydon xatolari |
| 429 | Juda ko‘p so‘rov | Rate limit va tiklanish vaqti |
| 500 | Qayta ishlanmagan server xatosi | Request ID va log |
| 502/503/504 | Servis yoki bog‘liqlik ishlamaydi | Health, deploy, tashqi tizim |

Muvaffaqiyatli HTTP kodi muvaffaqiyatli biznes natijasini isbotlamaydi.
Saqlangan ma’lumotlarni doimo tekshiring.

### Tizimga kirib bo‘lmasa

1. Staging URL va akkaunt rolini tekshiring.
2. Akkaunt faol ekaniga ishonch hosil qiling.
3. Network’dagi login so‘rovi va uning kodini tekshiring.
4. Noto‘g‘ri parol va mavjud bo‘lmagan foydalanuvchi xatolarini solishtiring.
5. Rate limit ishga tushmaganini tekshiring.
6. Qiymatlarni ko‘chirmasdan refresh/cookie’ni faqat lokal tekshiring.
7. Toza private oynada urinib ko‘ring.
8. Xato UI’dami yoki API’ning o‘zidami, qayd eting.

### Navbat 0 ko‘rsatsa

Quyidagi tartibda tekshiring:

1. Operator smenani boshlagan.
2. Operator kerakli voronkaga biriktirilgan.
3. Voronka tanlangan va sinxronlangan.
4. Lidda test telefoni bor.
5. Status tizim tomonidan taniladi.
6. Keyingi qo‘ng‘iroq vaqti kelgan.
7. Lid ish vaqtidan tashqarida emas.
8. Urinishlar soni to‘rttadan kam.
9. Lid yakuniy holatda emas va o‘chirilmagan.
10. Faol blok yoki yopilmagan sessiya yo‘q.
11. Lid to‘g‘ri kompaniyaga tegishli.

Kengaytirilgan checklist:
[«Lid nima uchun yo‘qolishi mumkin»](../02-lead-status-glossary.md#11-чек-лист-почему-лид-может-пропасть-из-обзвона).

### Qo‘ng‘iroq boshlanmasa

1. WebRTC yoki click-to-call ishlatilayotganini tekshiring.
2. Test raqami va qo‘ng‘iroq yo‘nalishini tekshiring.
3. Operator’ning ichki raqami to‘ldirilganiga ishonch hosil qiling.
4. Ichki raqam OnlinePBX’da yoqilganini tekshiring.
5. OnlinePBX konfiguratsiyasi faolligini tekshiring.
6. Chiquvchi so‘rov va telefoniya javobini toping.
7. Qo‘ng‘iroq sessiyasi yaratilganini va blok muddati tugamaganini tekshiring.
8. Raqam test raqami ekaniga ishonch hosil qilmaguningizcha qo‘ng‘iroqni ko‘p
   marta takrorlamang.

### Yozuv yoki AI natijasi bo‘lmasa

Zanjirni qismlarga ajrating:

```text
Qo‘ng‘iroq tugadi
  → OnlinePBX hodisasi olindi
  → yozuv mavjud
  → audio saqlandi
  → transkripsiya boshlandi
  → Gemini javob berdi
  → maydonlar saqlandi
  → UI natijani oldi
```

Tekshiring:

- suhbatga javob berilganmi va `dialog_duration` bormi;
- webhook kelganmi va dubl bo‘lmaganmi;
- zaxira polling ishlaganmi;
- yozuv havolasi mavjudmi;
- Gemini kvotasi/xatosi yo‘qmi;
- kalit logga tushmaganmi;
- retry tugamaganmi;
- javob forma maydonlariga mosmi;
- mijoz tomondagi kutish taymeri tugamaganmi.

Batafsil nosozlik nuqtalari:
[qo‘ng‘iroq yo‘li, 6-bo‘lim](../04-call-flow.md#6-где-процесс-может-сломаться-карта-отказов).

### Natija AmoCRM’da ko‘rinmasa

1. Operator formani haqiqatan tasdiqlaganini tekshiring.
2. Bitta yuborish so‘rovi va javobini qayd eting.
3. AmoCRM konfiguratsiyasi faol ekanini tekshiring.
4. To‘g‘ri kompaniya va voronkani tekshiring.
5. Yangi lid yaratilmay, dastlabki lid yangilanayotganiga ishonch hosil qiling.
6. Pipeline/status ID’larini solishtiring.
7. `Operator AI` guruhi maydonlarini tekshiring.
8. Select qiymati to‘g‘ri enum ID bilan yuborilayotganini tekshiring.
9. Lid holatini test AmoCRM’ning o‘zida tekshiring.
10. O‘qishni takrorlang, ammo idempotentlikni tekshirmasdan o‘zgartiruvchi
    so‘rovni qayta yubormang.

### UI eski yoki boshqa kompaniya ma’lumotini ko‘rsatsa

- joriy sessiya roli va tenant’ini tekshiring;
- so‘rov parametrlari va filtrlarni tekshiring;
- foydalanuvchini almashtirgandan keyin TanStack Query cache’ini tekshiring;
- SSE oqimi logout’dan keyin yopilishini tekshiring;
- private oynada takrorlang;
- logout’dan keyin Back tugmasini tekshiring;
- API javobi va UI ko‘rinishini solishtiring;
- boshqa kompaniya ma’lumoti bo‘lsa, to‘xtang va xavfsizlik muammosi sifatida
  eskalatsiya qiling.

### Dasturchiga nimani biriktirish kerak

Minimal diagnostika paketi:

```text
Vaqt va vaqt zonasi:
Muhit va versiya:
Rol va test kompaniya:
Keys ID:
Obyekt ID:
Oxirgi muvaffaqiyatli qadam:
Birinchi buzilgan qadam:
Request method/path/status:
Request/correlation ID:
Response’ning xavfsiz qismi:
Console:
Takrorlanish:
Skrinshot/video:
```

Dasturchiga vaqt, request ID va harakat tavsifisiz «loglarni ko‘ring» deb
yubormang.
