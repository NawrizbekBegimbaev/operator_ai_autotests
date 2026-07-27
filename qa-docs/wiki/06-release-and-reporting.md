# Релиз, Release Gate и отчёт

[← Баги и вопросы](05-defects-and-questions.md) · [Главная](../README.md) ·
[Далее: диагностика →](07-diagnostics.md)

## Что делает QA перед релизом

QA не обещает абсолютное отсутствие любых багов. QA предоставляет
проверяемые доказательства и рекомендацию:

- `GO` — обязательные условия выполнены;
- `NO-GO` — есть release blocker или не выполнено обязательное условие;
- `GO WITH RISKS` — только если владелец продукта письменно принял конкретный
  некритический риск и обходной путь.

Полная действующая матрица:
[«Карта покрытия и допуск клиентов»](../08-release-readiness.md).

## Definition of Ready для тестирования

Версия готова к подробному тестированию, если:

- определён состав релиза;
- указаны commit SHA Backend/Admin/Landing;
- версия развернута на staging;
- миграции и конфигурация применены;
- `/healthz` и `/readyz` успешны;
- доступны тестовые аккаунты трёх ролей;
- готовы тестовые AmoCRM и OnlinePBX;
- известны изменения и затронутые модули;
- подготовлены тестовые данные;
- нет параллельного деплоя в момент прогона.

Если Ready не выполнен, QA сообщает о блокере до начала полного регресса.

## Текущий обязательный набор

| Часть | Количество | Как учитывается |
| --- | ---: | --- |
| Активные кейсы | 385 | Обязательны для текущего полного релиза |
| Отложенные кейсы | 15 | Не входят в процент, пока функция не выпущена |
| Всего | 400 | Полный дизайн текущего продукта и утверждённого будущего |

Если отложенная функция стала видна клиенту, её кейсы переводятся в активные
и проходят до выпуска.

## Release Gate

Рекомендация `GO` возможна, только если одновременно:

1. все активные кейсы выполнены;
2. все Critical и High имеют `Passed`;
3. в активном наборе нет `Not Run` и `Blocked`;
4. нет открытых P0/P1;
5. P2 либо исправлены, либо письменно приняты владельцем продукта;
6. пройдены TC-351, TC-352 и TC-354;
7. пройдены клиентские сквозные TC-396, TC-397 и TC-398;
8. пройдены обязательные эксплуатационные и безопасностные кейсы,
   перечисленные в [Release Gate](../08-release-readiness.md#6-критерий-допуска-клиентов);
9. версия и окружение зафиксированы;
10. после исправлений выполнены retest, затронутый регресс и финальный smoke.

Если один пункт не выполнен, в отчёте нельзя писать «система полностью
проверена».

## Последовательность релизной проверки

1. Зафиксировать состав и версию.
2. Выполнить preflight.
3. Выполнить smoke.
4. Пройти Critical, затем High.
5. Выполнить остальные активные кейсы.
6. Зарегистрировать и провести triage дефектов.
7. Дождаться исправлений и выполнить retest.
8. Выполнить регресс затронутых модулей.
9. Пройти сквозные и эксплуатационные кейсы.
10. Сформировать отчёт и принять GO/NO-GO.
11. После выкладки выполнить согласованный production smoke только пассивными
    или специально разрешёнными безопасными действиями.
12. Наблюдать метрики и подготовить откат, если проявится критический сбой.

## Шаблон отчёта

```markdown
# Отчёт QA по релизу <версия>

Дата и время:
Окружение: staging
Backend SHA:
Admin SHA:
Landing SHA:
Конфигурация/миграция:
Ответственный QA:

## Объём

- Запланировано активных:
- Выполнено:
- Passed:
- Failed:
- Blocked:
- Not Run:

## Критические пути

- Авторизация и роли:
- Изоляция компаний:
- Очередь и звонок:
- OnlinePBX:
- AI:
- AmoCRM:
- Полный onboarding:
- Жизненный цикл лида:

## Дефекты

- P0:
- P1:
- P2:
- Принятые риски:

## Ограничения проверки

- Что не проверялось:
- Почему:
- Какой риск остаётся:

## Решение

GO / NO-GO / GO WITH RISKS

Обоснование:
Ссылка на Excel:
Ссылка на доказательства:
```

## Как формулировать вывод

Корректно:

> На указанной версии все известные требования, критические риски и
> клиентские сценарии из активного набора прошли приёмку. Открытых
> блокирующих дефектов нет. Релиз рекомендован.

Некорректно:

> В системе гарантированно нет багов.

Первое утверждение ограничено версией, окружением, данными и известным
покрытием. Второе невозможно доказать конечным числом тестов.

## После релиза

- проверь доступность и загрузку основных экранов;
- убедись, что новая версия действительно развернута;
- наблюдай рост 5xx, задержки, ошибки интеграций и перезапуски;
- не создавай реальные данные без отдельного production-сценария;
- при P0 активируй согласованный процесс инцидента и отката;
- зафиксируй найденные production-наблюдения отдельно от staging-результатов.

---

## O‘zbekcha versiya

[← Baglar va savollar](05-defects-and-questions.md) · [Asosiy sahifa](../README.md) ·
[Keyingi: diagnostika →](07-diagnostics.md)

### QA relizdan oldin nima qiladi

QA har qanday bag mutlaqo yo‘qligini va’da qilmaydi. QA tekshiriladigan
dalillar va tavsiya beradi:

- `GO` — barcha majburiy shartlar bajarilgan;
- `NO-GO` — release blocker bor yoki majburiy shart bajarilmagan;
- `GO WITH RISKS` — faqat mahsulot egasi muayyan nokritik xatar va
  vaqtinchalik yechimni yozma ravishda qabul qilgan bo‘lsa.

To‘liq amaldagi matritsa:
[«Qamrov xaritasi va mijozlarga ruxsat»](../08-release-readiness.md).

### Testlash uchun Definition of Ready

Versiya quyidagi shartlarda batafsil testlashga tayyor:

- reliz tarkibi aniqlangan;
- Backend/Admin/Landing commit SHA’lari ko‘rsatilgan;
- versiya staging’ga joylangan;
- migratsiya va konfiguratsiya qo‘llangan;
- `/healthz` va `/readyz` muvaffaqiyatli;
- uchala rolning test akkauntlari mavjud;
- test AmoCRM va OnlinePBX tayyor;
- o‘zgarishlar va ta’sirlangan modullar ma’lum;
- test ma’lumotlari tayyorlangan;
- test vaqtida parallel deploy yo‘q.

Ready bajarilmagan bo‘lsa, QA to‘liq regress boshlanishidan oldin bloklovchi
sabab haqida xabar beradi.

### Joriy majburiy to‘plam

| Qism | Soni | Qanday hisoblanadi |
| --- | ---: | --- |
| Faol keyslar | 385 | Joriy to‘liq reliz uchun majburiy |
| Kechiktirilgan keyslar | 15 | Funksiya chiqarilmaguncha foizga kirmaydi |
| Jami | 400 | Joriy mahsulot va tasdiqlangan kelajakning to‘liq dizayni |

Kechiktirilgan funksiya mijozga ko‘rinsa, uning keyslari faol holatga
o‘tkaziladi va relizgacha bajariladi.

### Release Gate

`GO` tavsiyasi faqat quyidagi shartlarning barchasi bir vaqtda bajarilsa
berilishi mumkin:

1. barcha faol keyslar bajarilgan;
2. barcha Critical va High statusi `Passed`;
3. faol to‘plamda `Not Run` va `Blocked` yo‘q;
4. ochiq P0/P1 yo‘q;
5. P2 tuzatilgan yoki mahsulot egasi tomonidan yozma qabul qilingan;
6. TC-351, TC-352 va TC-354 o‘tgan;
7. mijozning end-to-end TC-396, TC-397 va TC-398 keyslari o‘tgan;
8. [Release Gate’da](../08-release-readiness.md#6-критерий-допуска-клиентов)
   ko‘rsatilgan majburiy ekspluatatsion va xavfsizlik keyslari o‘tgan;
9. versiya va muhit qayd etilgan;
10. tuzatishlardan keyin retest, ta’sirlangan regress va yakuniy smoke
    bajarilgan.

Bitta band bajarilmasa, hisobotda «tizim to‘liq tekshirildi» deb yozish mumkin
emas.

### Reliz tekshiruvi ketma-ketligi

1. Tarkib va versiyani qayd etish.
2. Preflight bajarish.
3. Smoke bajarish.
4. Avval Critical, keyin High’ni bajarish.
5. Qolgan faol keyslarni bajarish.
6. Nuqsonlarni ro‘yxatdan o‘tkazish va triage qilish.
7. Tuzatishlarni kutish va retest bajarish.
8. Ta’sirlangan modullar regressini bajarish.
9. End-to-end va ekspluatatsion keyslarni bajarish.
10. Hisobot tuzish va GO/NO-GO qarorini qabul qilish.
11. Relizdan keyin production smoke’ni faqat passiv yoki maxsus ruxsat
    berilgan xavfsiz harakatlar bilan bajarish.
12. Metrikalarni kuzatish va kritik nosozlik chiqsa rollback tayyorlash.

### Hisobot shabloni

```markdown
# <versiya> relizi bo‘yicha QA hisoboti

Sana va vaqt:
Muhit: staging
Backend SHA:
Admin SHA:
Landing SHA:
Konfiguratsiya/migratsiya:
Mas’ul QA:

## Hajm

- Rejalashtirilgan faol keyslar:
- Bajarilgan:
- Passed:
- Failed:
- Blocked:
- Not Run:

## Kritik yo‘llar

- Avtorizatsiya va rollar:
- Kompaniyalar izolyatsiyasi:
- Navbat va qo‘ng‘iroq:
- OnlinePBX:
- AI:
- AmoCRM:
- To‘liq onboarding:
- Lid hayot sikli:

## Nuqsonlar

- P0:
- P1:
- P2:
- Qabul qilingan xatarlar:

## Tekshiruv cheklovlari

- Nima tekshirilmadi:
- Nima uchun:
- Qanday xatar qoladi:

## Qaror

GO / NO-GO / GO WITH RISKS

Asos:
Excel havolasi:
Dalillar havolasi:
```

### Xulosani qanday ifodalash kerak

To‘g‘ri:

> Ko‘rsatilgan versiyada faol to‘plamdagi barcha ma’lum talablar, kritik
> xatarlar va mijoz ssenariylari qabul qilish tekshiruvidan o‘tdi. Ochiq
> bloklovchi nuqsonlar yo‘q. Reliz tavsiya etiladi.

Noto‘g‘ri:

> Tizimda bag yo‘qligi kafolatlanadi.

Birinchi bayonot versiya, muhit, ma’lumotlar va ma’lum qamrov bilan
chegaralangan. Ikkinchisini cheklangan testlar soni bilan isbotlab bo‘lmaydi.

### Relizdan keyin

- asosiy ekranlarning mavjudligi va yuklanishini tekshiring;
- yangi versiya haqiqatan joylanganiga ishonch hosil qiling;
- 5xx o‘sishi, kechikishlar, integratsiya xatolari va restartlarni kuzating;
- alohida production ssenariysisiz haqiqiy ma’lumot yaratmang;
- P0 bo‘lsa, kelishilgan incident va rollback jarayonini ishga tushiring;
- production’da topilgan kuzatuvlarni staging natijalaridan alohida qayd eting.
