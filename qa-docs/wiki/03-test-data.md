# Тестовые данные

[← Окружения](02-environments-and-access.md) · [Главная](../README.md) ·
[Далее: ручное тестирование →](04-manual-testing.md)

## Зачем управлять тестовыми данными

Плохие тестовые данные создают ложные баги. Например, лид не попадает в
очередь не из-за кода, а потому что у него нет телефона, оператор не назначен
на воронку или уже использованы четыре попытки.

У каждого набора данных должны быть:

- назначение;
- владелец;
- дата создания;
- связанный тест-кейс;
- способ очистки;
- отметка, можно ли использовать повторно.

## Правило именования

Используй формат:

```text
QA-<дата>-<инициалы>-<ID кейса>-<назначение>
```

Примеры:

```text
QA-20260727-NB-TC044-ROP
QA-20260727-NB-TC352-no-answer
QA-20260727-NB-TC354-pipeline-A
```

Телефон, логин и другие уникальные поля формируй по согласованному правилу
стенда. Не придумывай случайный номер: он может принадлежать реальному
человеку.

## Минимальная матрица данных

| Набор | Для чего |
| --- | --- |
| Super-admin | Управление клиентами, тарифами и проверка прав |
| ROP-A и ROP-B | Изоляция двух компаний |
| Operator-A1 и Operator-A2 | Конкуренция внутри одной компании |
| Operator-B1 | Попытка доступа к данным другой компании |
| Тестовая воронка A | Основные статусы и поля Operator AI |
| Тестовая воронка B | Проверка, что статусы и поля не смешиваются |
| Лид без истории | Успешный путь нового лида |
| Лид с недозвоном | Попытки и повторная выдача |
| Лид со встречей | Дата/время и приоритет `Bugun` |
| Лид 3/4 попытки | Переход к `Sifatsiz` на четвёртой |
| Лид без телефона | Негативная синхронизация без остановки остальных |
| Тестовая запись звонка | Транскрипция и AI без персональных данных |

Один и тот же лид нельзя бесконтрольно использовать в нескольких кейсах:
предыдущий прогон меняет статус, число попыток, блокировку и историю.

## Подготовка данных к кейсу

1. Прочитай предусловия полностью.
2. Проверь компанию, роль, воронку и статус.
3. Запиши исходные ID сущностей.
4. Убедись, что лид не заблокирован незакрытой сессией.
5. Проверь число попыток и время следующего действия.
6. Убедись, что телефон тестовый.
7. Зафиксируй исходное состояние скриншотом или API-ответом.
8. Только после этого выполняй первый шаг кейса.

## Изоляция компаний

Для проверок tenant isolation всегда используй минимум две компании.

Безопасный шаблон:

1. Создай сущность под ROP-A.
2. Запиши её ID.
3. Убедись, что ROP-A и Operator-A видят только разрешённые данные.
4. Попробуй прочитать тот же ID под ROP-B и Operator-B.
5. Ожидай `403` или безопасный `404` без раскрытия полей сущности.
6. Проверь не только чтение, но и изменение/удаление, если это предусмотрено
   кейсом и согласовано.
7. Убедись, что не произошло побочного изменения.

Если чужие данные появились хотя бы частично, останови прогон и эскалируй как
возможный дефект безопасности.

## Данные для жизненного цикла

Перед проверкой статуса учитывай:

- название статуса может быть произвольным у каждого клиента;
- система распознаёт класс по ключевым словам;
- порядок распознавания влияет на результат;
- статус относится к конкретной воронке;
- четыре попытки считаются за весь жизненный цикл;
- время и рабочие часы влияют на очередь;
- `Sifatsiz` должен существовать в тестовой AmoCRM для финального перехода.

Полные правила:
[глоссарий статусов](../02-lead-status-glossary.md).

## Журнал созданных данных

Для большого прогона веди таблицу в отчёте или защищённом рабочем документе:

| Дата | Автор | Кейс | Тип | ID | Компания/воронка | Исходное состояние | Что изменено | Очистка |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 27.07.2026 | NB | TC-XXX | lead | `<id>` | QA ROP-A / Pipeline-A | Yangi, 0/4 | один недозвон | вернуть/удалить после прогона |

Не вставляй в таблицу токены, пароли, полный телефон или персональные данные.

## Очистка после прогона

- Удаляй только сущности с подтверждённым QA-префиксом.
- Сначала сверяй ID и компанию.
- Не выполняй массовое удаление по широкому фильтру.
- Если кейс проверяет историю или аудит, не очищай данные до ревью.
- Если безопасного удаления нет, пометь сущность как тестовую и передай
  ответственному список ID.
- Восстанови изменённую конфигурацию, если это было частью согласованного
  теста.
- Отметь очистку в журнале.

## Запрещённые данные

- реальные телефоны клиентов;
- реальные записи разговоров без отдельного разрешения;
- production-экспорт;
- личные аккаунты сотрудников;
- секреты интеграций;
- данные, источник и владелец которых неизвестны.

---

## O‘zbekcha versiya

[← Muhitlar](02-environments-and-access.md) · [Asosiy sahifa](../README.md) ·
[Keyingi: qo‘lda testlash →](04-manual-testing.md)

### Nima uchun test ma’lumotlarini boshqarish kerak

Yomon test ma’lumotlari yolg‘on baglar hosil qiladi. Masalan, lid koddagi xato
sababli emas, balki telefoni yo‘qligi, operator voronkaga biriktirilmagani yoki
to‘rtta urinish allaqachon ishlatilgani sababli navbatga tushmasligi mumkin.

Har bir ma’lumotlar to‘plamida quyidagilar bo‘lishi kerak:

- vazifa;
- egasi;
- yaratilgan sana;
- bog‘liq test-keys;
- tozalash usuli;
- qayta ishlatish mumkinligi haqidagi belgi.

### Nomlash qoidasi

Quyidagi formatdan foydalaning:

```text
QA-<sana>-<initsiallar>-<keys ID>-<vazifa>
```

Misollar:

```text
QA-20260727-NB-TC044-ROP
QA-20260727-NB-TC352-no-answer
QA-20260727-NB-TC354-pipeline-A
```

Telefon, login va boshqa noyob maydonlarni stendning kelishilgan qoidasi
bo‘yicha yarating. Tasodifiy raqam o‘ylab topmang: u haqiqiy insonga tegishli
bo‘lishi mumkin.

### Minimal ma’lumotlar matritsasi

| To‘plam | Nima uchun |
| --- | --- |
| Super-admin | Mijozlar, tariflar va huquqlarni boshqarishni tekshirish |
| ROP-A va ROP-B | Ikki kompaniya izolyatsiyasi |
| Operator-A1 va Operator-A2 | Bitta kompaniya ichidagi parallel ishlash |
| Operator-B1 | Boshqa kompaniya ma’lumotlariga kirishga urinish |
| Test voronkasi A | Operator AI’ning asosiy status va maydonlari |
| Test voronkasi B | Status va maydonlar aralashib ketmasligini tekshirish |
| Tarixsiz lid | Yangi lidning muvaffaqiyatli yo‘li |
| Javobsiz qo‘ng‘iroqli lid | Urinishlar va qayta berish |
| Uchrashuvli lid | Sana/vaqt va `Bugun` ustuvorligi |
| 3/4 urinishli lid | To‘rtinchi urinishda `Sifatsiz`ga o‘tish |
| Telefonsiz lid | Qolgan jarayonlarni to‘xtatmasdan negativ sinxronlash |
| Test qo‘ng‘iroq yozuvi | Shaxsiy ma’lumotlarsiz transkripsiya va AI |

Bitta lidni bir nechta keysda nazoratsiz ishlatish mumkin emas: oldingi test
status, urinishlar soni, blok va tarixni o‘zgartiradi.

### Keys uchun ma’lumot tayyorlash

1. Precondition’larni to‘liq o‘qing.
2. Kompaniya, rol, voronka va statusni tekshiring.
3. Obyektlarning dastlabki ID’larini yozing.
4. Lid yopilmagan sessiya bilan bloklanmaganiga ishonch hosil qiling.
5. Urinishlar soni va keyingi harakat vaqtini tekshiring.
6. Telefon test raqami ekaniga ishonch hosil qiling.
7. Dastlabki holatni skrinshot yoki API javobi bilan qayd eting.
8. Faqat shundan keyin keysning birinchi qadamini bajaring.

### Kompaniyalarni izolyatsiya qilish

Tenant isolation tekshiruvlari uchun doimo kamida ikkita kompaniyadan
foydalaning.

Xavfsiz shablon:

1. ROP-A ostida obyekt yarating.
2. Uning ID’sini yozing.
3. ROP-A va Operator-A faqat ruxsat berilgan ma’lumotlarni ko‘rishiga ishonch
   hosil qiling.
4. Shu ID’ni ROP-B va Operator-B ostida o‘qishga urinib ko‘ring.
5. Obyekt maydonlari oshkor bo‘lmasdan `403` yoki xavfsiz `404` kuting.
6. Agar keysda ko‘zda tutilgan va kelishilgan bo‘lsa, faqat o‘qishni emas,
   o‘zgartirish/o‘chirishni ham tekshiring.
7. Yon ta’sir sodir bo‘lmaganiga ishonch hosil qiling.

Boshqa kompaniya ma’lumotlari qisman bo‘lsa ham ko‘rinsa, testni to‘xtating va
ehtimoliy xavfsizlik nuqsoni sifatida eskalatsiya qiling.

### Hayot sikli uchun ma’lumotlar

Statusni tekshirishdan oldin quyidagilarni hisobga oling:

- status nomi har bir mijozda ixtiyoriy bo‘lishi mumkin;
- tizim klassni kalit so‘zlar orqali taniydi;
- tanib olish tartibi natijaga ta’sir qiladi;
- status muayyan voronkaga tegishli;
- to‘rtta urinish butun hayot sikli bo‘yicha hisoblanadi;
- vaqt va ish soatlari navbatga ta’sir qiladi;
- yakuniy o‘tish uchun test AmoCRM’da `Sifatsiz` mavjud bo‘lishi kerak.

To‘liq qoidalar:
[statuslar lug‘ati](../02-lead-status-glossary.md).

### Yaratilgan ma’lumotlar jurnali

Katta test uchun hisobotda yoki himoyalangan ish hujjatida jadval yuriting:

| Sana | Muallif | Keys | Tur | ID | Kompaniya/voronka | Dastlabki holat | Nima o‘zgardi | Tozalash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 27.07.2026 | NB | TC-XXX | lead | `<id>` | QA ROP-A / Pipeline-A | Yangi, 0/4 | bitta javobsiz qo‘ng‘iroq | testdan keyin qaytarish/o‘chirish |

Jadvalga tokenlar, parollar, to‘liq telefon yoki shaxsiy ma’lumotlarni
joylamang.

### Testdan keyin tozalash

- Faqat tasdiqlangan QA prefiksiga ega obyektlarni o‘chiring.
- Avval ID va kompaniyani solishtiring.
- Keng filtr bo‘yicha ommaviy o‘chirishni bajarmang.
- Keys tarix yoki auditni tekshirsa, ko‘rib chiqishdan oldin ma’lumotlarni
  tozalamang.
- Xavfsiz o‘chirish usuli bo‘lmasa, obyektni test ma’lumoti deb belgilang va
  mas’ulga ID’lar ro‘yxatini bering.
- Kelishilgan test doirasida o‘zgartirilgan konfiguratsiyani tiklang.
- Tozalashni jurnalda belgilang.

### Taqiqlangan ma’lumotlar

- mijozlarning haqiqiy telefonlari;
- alohida ruxsatsiz haqiqiy suhbat yozuvlari;
- production eksporti;
- xodimlarning shaxsiy akkauntlari;
- integratsiya sirlari;
- manbasi va egasi noma’lum ma’lumotlar.
