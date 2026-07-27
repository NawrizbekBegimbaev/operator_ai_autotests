# Баги, вопросы и повторная проверка

[← Ручное тестирование](04-manual-testing.md) · [Главная](../README.md) ·
[Далее: релиз →](06-release-and-reporting.md)

## Сначала определи тип находки

| Ситуация | Что создать |
| --- | --- |
| Ожидание однозначно, факт отличается | Баг |
| Диаграмма и код расходятся, но на staging ещё не проверено | Наблюдение/вопрос, затем воспроизведение |
| Непонятно, какое поведение правильное | Вопрос Q-XX |
| Стенд или внешний сервис недоступен | Блокер окружения |
| Есть идея по улучшению, но текущее поведение соответствует требованию | Предложение, не баг |

Главное правило проекта: баг регистрируется после самостоятельного
воспроизведения. Чтение подозрительного кода даёт гипотезу, а не доказанный
дефект.

## Перед созданием бага

- [ ] Повтори проблему минимум ещё один раз.
- [ ] Начни с чистого и понятного состояния.
- [ ] Проверь роль, компанию, окружение и версию.
- [ ] Убедись, что тестовые данные соответствуют предусловиям.
- [ ] Проверь Console и Network.
- [ ] Сравни с актуальной диаграммой и картой скоупа.
- [ ] Поищи существующий BUG-XXX или Q-XX.
- [ ] Проверь, воспроизводится ли в другом браузере, если это UI.
- [ ] Удали секреты и персональные данные из вложений.

Для критической утечки, потери данных или массовой недоступности не жди
полного оформления: сначала эскалируй, затем документируй.

## Хорошее название бага

Формула:

```text
<Где> + <при каком условии> + <что произошло неправильно>
```

Хорошо:

```text
Очередь выдаёт один лид двум операторам при одновременном запросе
```

Плохо:

```text
Не работает очередь
```

## Обязательные поля

Полный шаблон находится в
[журнале багов](../05-bugs.md#шаблон-копировать-отсюда).

Баг должен содержать:

1. окружение и проверяемую версию;
2. браузер/ОС или способ API-проверки;
3. роль и тестовую компанию;
4. предусловия;
5. минимальные шаги с нуля;
6. ожидаемый результат со ссылкой на источник;
7. фактический результат без догадок о причине;
8. повторяемость;
9. приоритет;
10. безопасное доказательство;
11. связанные TC/Q/DGM.

## Приоритет

| Приоритет | Значение | Пример |
| --- | --- | --- |
| P0 | Авария или немедленный release blocker: массовая недоступность, потеря/утечка данных | Компания видит данные другого клиента |
| P1 | Критический путь не работает, безопасного обхода нет, серьёзная проблема прав | Operator не может войти или звонить |
| P2 | Значимая функция работает неверно, но есть временный обход | Поле нельзя сохранить одним способом |
| P3 | Небольшой или косметический дефект | Неверное выравнивание текста |

Приоритет показывает, когда исправлять с точки зрения бизнеса. Он не заменяет
описание технического влияния.

Junior не обязан самостоятельно принимать спорное решение P0/P1. Он должен
собрать факты и быстро эскалировать.

## Как оформить вопрос

Если ожидание неизвестно, добавь Q-XX в
[журнал вопросов](../03-questions-for-team.md):

```text
Контекст:
Что показывает диаграмма:
Что делает текущий код/staging:
Конкретный вопрос:
Почему ответ влияет на клиента или тестирование:
Связанные кейсы:
Кому адресован вопрос:
```

Вопрос считается закрытым только после фиксации ответа. Из ответа должно
родиться одно из действий:

- обновить тест-кейс;
- зарегистрировать баг;
- обновить карту скоупа;
- отметить функцию отложенной;
- снять вопрос как неактуальный.

Устный ответ, который нигде не записан, не является стабильным требованием.

## Дефекты безопасности

Если обнаружены чужие данные, обход роли, активная сессия выключенного
пользователя или секрет в логах:

1. останови дальнейшее исследование;
2. не скачивай лишние данные;
3. сохрани минимальное доказательство;
4. сообщи ответственным через закрытый канал;
5. не публикуй токен, пароль или полный payload;
6. зарегистрируй ограниченный баг с пометкой безопасности;
7. дождись инструкции перед дополнительным воспроизведением.

## Повторная проверка исправления

`Исправлен разработчиком` не означает `Проверен QA`.

При retest:

1. зафиксируй новую версию;
2. повтори исходные шаги на исходных условиях;
3. проверь ожидаемый результат;
4. проверь негативный вариант рядом с исправлением;
5. выполни затронутый регресс;
6. убедись, что нет побочных изменений;
7. приложи новое доказательство;
8. только после этого закрой баг.

Если исходный дефект исчез, но появился другой, старый баг можно закрыть, а
новый зарегистрировать отдельно. Не переписывай историю исходной проблемы.

## Связь артефактов

У хорошей находки прослеживается цепочка:

```text
Требование/диаграмма
        ↓
Тест-кейс TC-XXX
        ↓
Баг BUG-XXX или вопрос Q-XX
        ↓
Исправление и commit
        ↓
Retest + регресс
        ↓
Решение по релизу
```

Эта связь позволяет новому QA понять не только что сломалось, но и почему
именно это важно.

---

## O‘zbekcha versiya

[← Qo‘lda testlash](04-manual-testing.md) · [Asosiy sahifa](../README.md) ·
[Keyingi: reliz →](06-release-and-reporting.md)

### Avval topilma turini aniqlang

| Holat | Nima yaratish kerak |
| --- | --- |
| Kutilgan natija aniq, fakt esa boshqacha | Bag |
| Diagramma va kod farq qiladi, ammo staging’da hali tekshirilmagan | Kuzatuv/savol, keyin takrorlash |
| Qaysi xatti-harakat to‘g‘ri ekanligi noma’lum | Q-XX savoli |
| Stend yoki tashqi servis ishlamaydi | Muhit bloklovchisi |
| Yaxshilash g‘oyasi bor, ammo joriy xatti-harakat talabga mos | Taklif, bag emas |

Loyihaning asosiy qoidasi: bag mustaqil ravishda takrorlangandan keyin
ro‘yxatdan o‘tkaziladi. Shubhali kodni o‘qish gipoteza beradi, isbotlangan
nuqson emas.

### Bag yaratishdan oldin

- [ ] Muammoni kamida yana bir marta takrorlang.
- [ ] Toza va tushunarli holatdan boshlang.
- [ ] Rol, kompaniya, muhit va versiyani tekshiring.
- [ ] Test ma’lumotlari precondition’larga mosligiga ishonch hosil qiling.
- [ ] Console va Network’ni tekshiring.
- [ ] Amaldagi diagramma va scope xaritasi bilan solishtiring.
- [ ] Mavjud BUG-XXX yoki Q-XX’ni qidiring.
- [ ] UI muammosi bo‘lsa, boshqa brauzerda takrorlanishini tekshiring.
- [ ] Ilovalardan sirlar va shaxsiy ma’lumotlarni olib tashlang.

Kritik ma’lumot sizib chiqishi, ma’lumot yo‘qolishi yoki ommaviy ishlamaslik
holatida to‘liq rasmiylashtirishni kutmang: avval eskalatsiya qiling, keyin
hujjatlashtiring.

### Yaxshi bag nomi

Formula:

```text
<Qayerda> + <qaysi shartda> + <nima noto‘g‘ri sodir bo‘ldi>
```

Yaxshi:

```text
Bir vaqtdagi so‘rovda navbat bitta lidni ikki operatorga beradi
```

Yomon:

```text
Navbat ishlamaydi
```

### Majburiy maydonlar

To‘liq shablon [baglar jurnalida](../05-bugs.md#шаблон-копировать-отсюда)
joylashgan.

Bag quyidagilarni o‘z ichiga olishi kerak:

1. muhit va tekshirilayotgan versiya;
2. brauzer/OS yoki API tekshirish usuli;
3. rol va test kompaniya;
4. precondition’lar;
5. noldan boshlab minimal qadamlar;
6. manbaga havola bilan kutilgan natija;
7. sabab haqida taxminsiz haqiqiy natija;
8. takrorlanish darajasi;
9. ustuvorlik;
10. xavfsiz dalil;
11. bog‘liq TC/Q/DGM.

### Ustuvorlik

| Ustuvorlik | Ma’nosi | Misol |
| --- | --- | --- |
| P0 | Avariya yoki darhol release blocker: ommaviy ishlamaslik, ma’lumot yo‘qolishi/sizib chiqishi | Kompaniya boshqa mijoz ma’lumotini ko‘radi |
| P1 | Kritik yo‘l ishlamaydi, xavfsiz vaqtinchalik yechim yo‘q, huquqlarda jiddiy muammo | Operator kira olmaydi yoki qo‘ng‘iroq qila olmaydi |
| P2 | Muhim funksiya noto‘g‘ri ishlaydi, ammo vaqtinchalik yechim bor | Maydonni bir usul bilan saqlab bo‘lmaydi |
| P3 | Kichik yoki kosmetik nuqson | Matn noto‘g‘ri tekislangan |

Ustuvorlik biznes nuqtayi nazaridan qachon tuzatish kerakligini ko‘rsatadi. U
texnik ta’sir tavsifini almashtirmaydi.

Junior bahsli P0/P1 qarorini mustaqil qabul qilishi shart emas. U faktlarni
yig‘ib, tez eskalatsiya qilishi kerak.

### Savolni qanday rasmiylashtirish kerak

Kutilgan natija noma’lum bo‘lsa, [savollar jurnaliga](../03-questions-for-team.md)
Q-XX qo‘shing:

```text
Kontekst:
Diagramma nimani ko‘rsatadi:
Joriy kod/staging nima qiladi:
Aniq savol:
Javob nima uchun mijoz yoki testlashga ta’sir qiladi:
Bog‘liq keyslar:
Savol kimga yo‘naltirilgan:
```

Savol faqat javob yozma qayd etilgandan keyin yopilgan hisoblanadi. Javobdan
quyidagi harakatlardan biri kelib chiqishi kerak:

- test-keysni yangilash;
- bagni ro‘yxatdan o‘tkazish;
- scope xaritasini yangilash;
- funksiyani kechiktirilgan deb belgilash;
- savolni dolzarb emas deb yopish.

Hech qayerda yozilmagan og‘zaki javob barqaror talab hisoblanmaydi.

### Xavfsizlik nuqsonlari

Boshqa kompaniya ma’lumoti, rolni chetlab o‘tish, o‘chirilgan
foydalanuvchining faol sessiyasi yoki logdagi sir aniqlansa:

1. keyingi tadqiqotni to‘xtating;
2. ortiqcha ma’lumot yuklab olmang;
3. minimal dalilni saqlang;
4. yopiq kanal orqali mas’ullarga xabar bering;
5. token, parol yoki to‘liq payload’ni e’lon qilmang;
6. xavfsizlik belgisi bilan cheklangan bag yarating;
7. qo‘shimcha takrorlashdan oldin ko‘rsatma kuting.

### Tuzatishni qayta tekshirish

`Dasturchi tuzatdi` degani `QA tekshirdi` degani emas.

Retest vaqtida:

1. yangi versiyani qayd eting;
2. dastlabki qadamlarni dastlabki shartlarda takrorlang;
3. kutilgan natijani tekshiring;
4. tuzatish yonidagi negativ variantni tekshiring;
5. ta’sirlangan regressni bajaring;
6. yon o‘zgarishlar yo‘qligiga ishonch hosil qiling;
7. yangi dalilni biriktiring;
8. faqat shundan keyin bagni yoping.

Dastlabki nuqson yo‘qolib, boshqa nuqson paydo bo‘lsa, eski bagni yopish va
yangisini alohida ro‘yxatdan o‘tkazish mumkin. Dastlabki muammo tarixini qayta
yozmang.

### Artefaktlar bog‘lanishi

Yaxshi topilmada quyidagi zanjir kuzatiladi:

```text
Talab/diagramma
        ↓
Test-keys TC-XXX
        ↓
Bag BUG-XXX yoki savol Q-XX
        ↓
Tuzatish va commit
        ↓
Retest + regress
        ↓
Reliz qarori
```

Bu bog‘lanish yangi QA’ga nafaqat nima buzilganini, balki nima uchun muhim
ekanini ham tushunishga yordam beradi.
