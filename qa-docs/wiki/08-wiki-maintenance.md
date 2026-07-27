# Как поддерживать QA Wiki

[← Диагностика](07-diagnostics.md) · [Главная QA Wiki](../README.md)

Wiki полезна только пока ей можно доверять. Старое уверенное утверждение
опаснее честной пометки «нужно уточнить».

## Что является источником, а что объяснением

Wiki объясняет процесс новым людям, но не заменяет:

- код;
- актуальные продуктовые диаграммы;
- карту скоупа;
- зафиксированные ответы команды;
- тест-кейсы и результаты прогона.

Если бизнес-правило изменилось, сначала обновляется источник и проверка, а
потом краткое объяснение в Wiki.

## Когда документацию нужно пересмотреть

- обновился Backend, Admin или Landing;
- изменилась одна из двух диаграмм;
- реализована фиолетовая функция;
- закрыт продуктовый вопрос Q-XX;
- воспроизведено расхождение DGM;
- изменился API-контракт;
- изменились роли или карта экранов;
- появился новый внешний сервис;
- изменился Release Gate;
- Junior не смог выполнить инструкцию без устного пояснения.

Последний пункт особенно важен: вопрос новичка — сигнал о дыре в Wiki.

## Порядок обновления

1. Зафиксируй новые commit SHA.
2. Сверь код с двумя актуальными диаграммами.
3. Обнови [карту скоупа](../06-scope-status.md).
4. Обнови подробный тематический документ.
5. Добавь или измени тест-кейсы в генераторе Excel.
6. Обнови связь requirement → TC → BUG/Q.
7. Измени краткое объяснение в Wiki.
8. Проверь все относительные ссылки.
9. Укажи дату сверки и рецензента.

Не обновляй только Wiki, если тест-кейс продолжает проверять старое правило.

## Стандарт страницы

Каждая новая страница должна отвечать на вопросы:

- для кого она;
- какую задачу помогает выполнить;
- какой источник подтверждает правила;
- когда её нужно обновлять;
- кто проверил изменение;
- куда перейти дальше.

Если отдельный владелец страницы не указан, действует владелец всей Wiki,
зафиксированный на [главной странице](../README.md).

Для инструкции используй:

1. предусловия;
2. конкретные действия;
3. ожидаемый результат;
4. опасные действия и точку остановки;
5. пример.

Избегай фраз «проверить корректность» и «убедиться, что всё работает» без
измеримого критерия.

## Правила языка

- Пиши по-русски простыми короткими предложениями.
- При первом использовании объясняй технический термин бытовым сравнением.
- Узбекский термин оставляй рядом с русским смыслом.
- Сохраняй кодовые названия ролей, статусов и API в обратных кавычках.
- Не используй разные слова для одной сущности без объяснения.
- Не копируй большой технический раздел в Wiki — поставь ссылку.
- После изменения русского раздела обновляй узбекский вариант на той же
  странице.

## Версионность

Для динамичного документа указывай:

```text
Последняя сверка:
Backend SHA:
Admin SHA:
Landing SHA:
Продуктовый источник:
Ответственный:
```

Результат тестирования без версии нельзя использовать для решения по новому
релизу.

## Устаревшие документы

- Не восстанавливай удалённые источники как действующие.
- Если документ заменён, явно укажи новый источник.
- Историческую информацию оставляй только когда она объясняет риск или
  регрессионный кейс.
- Устаревшее правило нельзя оставлять рядом с новым без заметной пометки.
- Секреты удаляются и ротируются, а не архивируются.

## Definition of Done для изменения документации

- [ ] Правило подтверждено источником.
- [ ] Указана версия кода.
- [ ] Нет противоречия с картой скоупа.
- [ ] Тест-кейсы обновлены.
- [ ] Отложенные функции не выданы за готовые.
- [ ] Ссылки открываются.
- [ ] Нет секретов и персональных данных.
- [ ] Текст понятен Junior без устного контекста.
- [ ] Узбекский вариант соответствует русскому разделу.
- [ ] Изменение проверил второй человек или назначенный ответственный.

## Как Junior предлагает исправление

Junior не обязан молча обходить непонятную инструкцию.

1. Запиши, на каком шаге возник вопрос.
2. Приведи конкретный пример.
3. Предложи новую формулировку.
4. Укажи источник, если меняется правило.
5. Передай изменение на ревью.

Хорошая Wiki создаётся всей QA-командой, но каждое бизнес-правило всё равно
должно иметь проверяемый источник.

---

## O‘zbekcha versiya

[← Diagnostika](07-diagnostics.md) · [Asosiy QA Wiki](../README.md)

Wiki faqat unga ishonish mumkin bo‘lgan vaqtgacha foydali. Eskirgan, ammo
ishonch bilan yozilgan bayonot «aniqlashtirish kerak» degan halol belgidan
xavfliroq.

### Nima manba, nima esa izoh

Wiki jarayonni yangi odamlarga tushuntiradi, ammo quyidagilarni almashtirmaydi:

- kod;
- amaldagi mahsulot diagrammalari;
- scope xaritasi;
- jamoaning qayd etilgan javoblari;
- test-keyslar va test natijalari.

Biznes qoida o‘zgarsa, avval manba va tekshiruv, keyin Wiki’dagi qisqa izoh
yangilanadi.

### Hujjatlarni qachon qayta ko‘rib chiqish kerak

- Backend, Admin yoki Landing yangilandi;
- ikki diagrammadan biri o‘zgardi;
- binafsha funksiya implementatsiya qilindi;
- Q-XX mahsulot savoli yopildi;
- DGM farqi takrorlandi;
- API shartnomasi o‘zgardi;
- rollar yoki ekranlar xaritasi o‘zgardi;
- yangi tashqi servis paydo bo‘ldi;
- Release Gate o‘zgardi;
- Junior og‘zaki izohsiz yo‘riqnomani bajara olmadi.

Oxirgi band ayniqsa muhim: yangi xodimning savoli Wiki’dagi bo‘shliq
signalidir.

### Yangilash tartibi

1. Yangi commit SHA’larni qayd eting.
2. Kodni ikki amaldagi diagramma bilan solishtiring.
3. [Scope xaritasini](../06-scope-status.md) yangilang.
4. Batafsil mavzuli hujjatni yangilang.
5. Excel generatorida test-keyslarni qo‘shing yoki o‘zgartiring.
6. Requirement → TC → BUG/Q bog‘lanishini yangilang.
7. Wiki’dagi qisqa izohni o‘zgartiring.
8. Barcha nisbiy havolalarni tekshiring.
9. Tekshiruv sanasi va reviewer’ni ko‘rsating.

Test-keys eski qoidani tekshirishda davom etsa, faqat Wiki’ni yangilamang.

### Sahifa standarti

Har bir yangi sahifa quyidagi savollarga javob berishi kerak:

- kim uchun;
- qanday vazifani bajarishga yordam beradi;
- qoidalarni qaysi manba tasdiqlaydi;
- qachon yangilanishi kerak;
- o‘zgarishni kim tekshirgan;
- keyin qayerga o‘tish kerak.

Alohida sahifa egasi ko‘rsatilmagan bo‘lsa, [asosiy sahifada](../README.md)
qayd etilgan butun Wiki egasi amal qiladi.

Yo‘riqnoma uchun quyidagilardan foydalaning:

1. precondition’lar;
2. aniq harakatlar;
3. kutilgan natija;
4. xavfli harakatlar va to‘xtash nuqtasi;
5. misol.

O‘lchanadigan mezonsiz «to‘g‘riligini tekshirish» va «hammasi ishlashiga
ishonch hosil qilish» iboralaridan qoching.

### Til qoidalari

- Ruscha matnni oddiy, qisqa gaplar bilan yozing.
- Texnik atama birinchi marta ishlatilganda uni kundalik o‘xshatish bilan
  tushuntiring.
- O‘zbekcha atamani ruscha ma’nosi yonida qoldiring.
- Rollar, statuslar va API kod nomlarini teskari qo‘shtirnoqda saqlang.
- Izohsiz bitta obyekt uchun turli so‘zlardan foydalanmang.
- Katta texnik bo‘limni Wiki’ga ko‘chirmang — havola bering.
- Ruscha qism o‘zgarsa, shu sahifadagi o‘zbekcha versiyani ham o‘sha
  o‘zgarish doirasida yangilang.

### Versiyalash

Dinamik hujjatda quyidagilarni ko‘rsating:

```text
Oxirgi tekshiruv:
Backend SHA:
Admin SHA:
Landing SHA:
Mahsulot manbasi:
Mas’ul:
```

Versiyasiz test natijasidan yangi reliz bo‘yicha qaror qabul qilishda
foydalanib bo‘lmaydi.

### Eskirgan hujjatlar

- O‘chirilgan manbalarni amaldagi sifatida qayta tiklamang.
- Hujjat almashtirilgan bo‘lsa, yangi manbani aniq ko‘rsating.
- Tarixiy ma’lumotni faqat u xatar yoki regress keysini tushuntirsa qoldiring.
- Eskirgan qoidani ko‘rinadigan belgisiz yangi qoida yonida qoldirmang.
- Sirlar arxivlanmaydi: ular o‘chiriladi va rotatsiya qilinadi.

### Hujjat o‘zgarishi uchun Definition of Done

- [ ] Qoida manba bilan tasdiqlangan.
- [ ] Kod versiyasi ko‘rsatilgan.
- [ ] Scope xaritasi bilan qarama-qarshilik yo‘q.
- [ ] Test-keyslar yangilangan.
- [ ] Kechiktirilgan funksiyalar tayyor deb ko‘rsatilmagan.
- [ ] Havolalar ochiladi.
- [ ] Sirlar va shaxsiy ma’lumotlar yo‘q.
- [ ] Matn Junior’ga og‘zaki kontekstsiz tushunarli.
- [ ] O‘zbekcha versiya ruscha qismga mos.
- [ ] O‘zgarishni ikkinchi shaxs yoki tayinlangan mas’ul tekshirgan.

### Junior qanday tuzatish taklif qiladi

Junior tushunarsiz yo‘riqnomani indamay chetlab o‘tishi shart emas.

1. Savol qaysi qadamda paydo bo‘lganini yozing.
2. Aniq misol keltiring.
3. Yangi ifodani taklif qiling.
4. Qoida o‘zgarsa, manbani ko‘rsating.
5. O‘zgarishni review’ga yuboring.

Yaxshi Wiki butun QA jamoasi tomonidan yaratiladi, ammo har bir biznes qoida
baribir tekshiriladigan manbaga ega bo‘lishi kerak.
