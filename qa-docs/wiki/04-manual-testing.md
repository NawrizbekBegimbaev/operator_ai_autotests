# Ручное тестирование

[← Тестовые данные](03-test-data.md) · [Главная](../README.md) ·
[Далее: баги и вопросы →](05-defects-and-questions.md)

Основной набор находится в
[07-test-cases.xlsx](../07-test-cases.xlsx). В нём 400 кейсов:
385 активных и 15 отложенных до реализации соответствующих функций.

## Как устроен Excel

| Колонка | Что означает |
| --- | --- |
| ID | Постоянный номер кейса |
| Раздел | Функциональная область |
| Экран / Подраздел | Экран, маршрут API или часть процесса |
| Сценарий | Что и зачем проверяется |
| Предусловия | Состояние до первого шага |
| Шаги | Действия по порядку |
| Ожидаемый результат | Единственный критерий успешности |
| Приоритет | Насколько опасна поломка |
| Статус | Результат выполнения |
| Комментарий | Теги, фактический результат, доказательство и баг |

Лист «Сводка» показывает покрытие, а «Прогресс и риски» — выполнение,
известные риски и Release Gate.

## Значение статусов

| Статус | Когда ставить | Пример |
| --- | --- | --- |
| `Passed` | Фактический результат полностью совпал с ожидаемым | Создана одна запись, поля и права верны |
| `Failed` | Продукт выполнил шаг, но результат отличается | Запись создалась дважды или видны чужие данные |
| `Blocked` | Проверку невозможно выполнить из-за внешней причины | Нет доступа, стенд не готов, выключена тестовая телефония |
| `Not Run` | Кейс ещё не выполнялся | До строки ещё не дошли |

Нельзя ставить `Passed`, если совпала только главная часть, а дополнительное
условие нет. Формулировка «в целом работает» не является результатом.

## Порядок выполнения одного кейса

1. Проверь, что работаешь на staging.
2. Запиши версию Backend, Admin и конфигурацию прогона.
3. Прочитай весь кейс до первого действия.
4. Подготовь предусловия и зафиксируй исходные ID.
5. Выполни шаги в указанном порядке.
6. Не добавляй действия «по смыслу», не записав их в комментарий.
7. Сравни каждый пункт ожидаемого результата с фактом.
8. Проверь побочные эффекты через UI и/или API.
9. Сохрани доказательство.
10. Поставь статус.
11. Для `Failed` укажи ID баг-репорта.
12. Очисти тестовые данные или запиши, почему они оставлены.

## Шаблон комментария

```text
27.07.2026 15:40 UZT | staging
Версия: back <sha>, admin <sha> | Chrome <version>
Факт: <что произошло, без оценки>
Доказательство: <ссылка/имя файла или request ID>
Данные: ROP-A, lead <безопасный ID>
Баг: BUG-XXX / нет
```

Начальные теги `web|api|positive|negative|boundary` удалять не нужно. После
них можно начать новую строку и дописать результат.

## Как выбрать Failed или Blocked

Используй простой вопрос:

```text
Система получила необходимые условия и выполнила проверяемое действие?
├─ Нет, потому что нет доступа/стенд недоступен/внешняя система выключена → Blocked
└─ Да
   └─ Результат отличается от ожидаемого → Failed
```

Примеры:

- API всего стенда возвращает 503 до начала кейса — `Blocked`;
- API работает, но конкретный валидный запрос возвращает 500 — `Failed`;
- нет тестового номера для звонка — `Blocked`;
- согласованный тестовый номер есть, но звонок не стартует — `Failed`;
- требование непонятно — временно `Blocked` и вопрос Q-XX, а не выдуманный
  `Passed` или `Failed`.

## Доказательства

Для UI обычно достаточно:

- скриншота с адресом/экраном и видимым результатом;
- короткого видео для анимации, гонки или последовательности;
- Console, если есть ошибка JavaScript;
- Network-запроса без секретных заголовков.

Для API сохраняй:

- метод и путь;
- безопасное тело запроса;
- HTTP-код;
- значимую часть ответа;
- request/correlation ID, если он есть;
- состояние сущности до и после.

Для интеграции проверяй обе стороны. Сообщение «успешно» в Operator AI не
доказывает, что AmoCRM действительно обновилась.

## Рекомендуемый порядок полного прогона

1. Preflight и smoke окружения.
2. Авторизация и сессии.
3. Роли и изоляция компаний.
4. Пользователи и настройки.
5. Лиды, статусы и очередь.
6. Цикл звонка.
7. OnlinePBX, AI и AmoCRM.
8. Смены, тарифы, локализация и Landing.
9. Сквозные и эксплуатационные кейсы.
10. Повторная проверка исправлений и затронутый регресс.

Если вход или изоляция компаний сломаны, нет смысла выполнять весь
последующий набор: сначала регистрируется блокирующий дефект и принимается
решение о продолжении.

## Smoke, регресс и исследовательская проверка

**Smoke** отвечает на вопрос «версия вообще пригодна для подробного
тестирования?». Он короткий и выполняется после каждого деплоя.

**Регресс** отвечает на вопрос «изменение не сломало ранее работавшее?».
Выбирается по затронутым модулям и рискам, а перед релизом расширяется до
полного обязательного набора.

**Исследовательская проверка** дополняет, но не заменяет тест-кейсы. На неё
задаётся ограничение по времени и цель, например: «30 минут исследовать
поведение очереди при двух вкладках». Все новые наблюдения фиксируются.

## Когда кейс нужно остановить

- обнаружено возможное раскрытие чужих данных;
- действие может уйти реальному клиенту;
- следующий шаг разрушителен и не согласован;
- фактическое состояние уже не соответствует предусловиям;
- требуется секрет, которого нет в защищённом хранилище;
- ожидание противоречиво;
- один дефект делает дальнейшие шаги недостоверными.

В комментарии укажи номер последнего выполненного шага и причину остановки.

---

## O‘zbekcha versiya

[← Test ma’lumotlari](03-test-data.md) · [Asosiy sahifa](../README.md) ·
[Keyingi: baglar va savollar →](05-defects-and-questions.md)

Asosiy to‘plam [07-test-cases.xlsx](../07-test-cases.xlsx) faylida joylashgan.
Unda 400 ta keys bor: 385 tasi faol, 15 tasi tegishli funksiyalar
implementatsiya qilinguncha kechiktirilgan.

### Excel qanday tuzilgan

| Ustun | Ma’nosi |
| --- | --- |
| ID | Keysning doimiy raqami |
| Раздел | Funksional soha |
| Экран / Подраздел | Ekran, API route yoki jarayon qismi |
| Сценарий | Nima va nima uchun tekshiriladi |
| Предусловия | Birinchi qadamgacha bo‘lgan holat |
| Шаги | Tartib bo‘yicha harakatlar |
| Ожидаемый результат | Muvaffaqiyatning yagona mezoni |
| Приоритет | Nosozlik qanchalik xavfli |
| Статус | Bajarish natijasi |
| Комментарий | Teglar, haqiqiy natija, dalil va bag |

«Сводка» varag‘i qamrovni, «Прогресс и риски» esa bajarilish holati, ma’lum
xatarlar va Release Gate’ni ko‘rsatadi.

### Statuslar ma’nosi

| Status | Qachon qo‘yiladi | Misol |
| --- | --- | --- |
| `Passed` | Haqiqiy natija kutilgan natijaga to‘liq mos keldi | Bitta yozuv yaratildi, maydonlar va huquqlar to‘g‘ri |
| `Failed` | Mahsulot qadamni bajardi, ammo natija boshqacha | Yozuv ikki marta yaratildi yoki boshqa kompaniya ma’lumoti ko‘rindi |
| `Blocked` | Tashqi sabab tufayli tekshiruvni bajarib bo‘lmaydi | Kirish yo‘q, stend tayyor emas, test telefoniyasi o‘chirilgan |
| `Not Run` | Keys hali bajarilmagan | Bu qatorgacha hali yetib kelinmagan |

Faqat asosiy qism mos kelib, qo‘shimcha shart bajarilmasa, `Passed` qo‘yish
mumkin emas. «Umuman olganda ishlaydi» iborasi natija hisoblanmaydi.

### Bitta keysni bajarish tartibi

1. Staging’da ishlayotganingizni tekshiring.
2. Backend, Admin versiyasi va test konfiguratsiyasini yozing.
3. Birinchi harakatdan oldin butun keysni o‘qing.
4. Precondition’larni tayyorlang va dastlabki ID’larni qayd eting.
5. Qadamlarni ko‘rsatilgan tartibda bajaring.
6. «Mazmuniga ko‘ra» qo‘shilgan harakatni izohga yozmasdan bajarmang.
7. Kutilgan natijaning har bir bandini fakt bilan solishtiring.
8. UI va/yoki API orqali yon ta’sirlarni tekshiring.
9. Dalilni saqlang.
10. Status qo‘ying.
11. `Failed` uchun bag-report ID’sini ko‘rsating.
12. Test ma’lumotlarini tozalang yoki nima uchun qoldirilganini yozing.

### Izoh shabloni

```text
27.07.2026 15:40 UZT | staging
Versiya: back <sha>, admin <sha> | Chrome <version>
Fakt: <bahosiz, nima sodir bo‘ldi>
Dalil: <havola/fayl nomi yoki request ID>
Ma’lumotlar: ROP-A, lead <xavfsiz ID>
Bag: BUG-XXX / yo‘q
```

Boshlang‘ich `web|api|positive|negative|boundary` teglarini o‘chirish shart
emas. Ulardan keyin yangi qatordan natijani yozish mumkin.

### Failed yoki Blocked’ni qanday tanlash kerak

Oddiy savoldan foydalaning:

```text
Tizim zarur shartlarni oldi va tekshirilayotgan harakatni bajardimi?
├─ Yo‘q, chunki kirish yo‘q/stend ishlamaydi/tashqi tizim o‘chirilgan → Blocked
└─ Ha
   └─ Natija kutilganidan farq qiladi → Failed
```

Misollar:

- keys boshlanishidan oldin butun stend API’si 503 qaytaradi — `Blocked`;
- API ishlaydi, ammo muayyan valid so‘rov 500 qaytaradi — `Failed`;
- qo‘ng‘iroq uchun test raqami yo‘q — `Blocked`;
- kelishilgan test raqami bor, ammo qo‘ng‘iroq boshlanmaydi — `Failed`;
- talab tushunarsiz — vaqtincha `Blocked` va Q-XX savoli; o‘ylab topilgan
  `Passed` yoki `Failed` emas.

### Dalillar

UI uchun odatda quyidagilar yetarli:

- manzil/ekran va ko‘rinadigan natijali skrinshot;
- animatsiya, race condition yoki ketma-ketlik uchun qisqa video;
- JavaScript xatosi bo‘lsa, Console;
- sirli sarlavhalarsiz Network so‘rovi.

API uchun quyidagilarni saqlang:

- metod va path;
- xavfsiz request body;
- HTTP kod;
- javobning muhim qismi;
- mavjud bo‘lsa request/correlation ID;
- obyektning oldingi va keyingi holati.

Integratsiya uchun ikki tomonni ham tekshiring. Operator AI’dagi
«muvaffaqiyatli» xabari AmoCRM haqiqatan yangilanganini isbotlamaydi.

### To‘liq testning tavsiya etilgan tartibi

1. Muhit preflight va smoke tekshiruvi.
2. Avtorizatsiya va sessiyalar.
3. Rollar va kompaniyalar izolyatsiyasi.
4. Foydalanuvchilar va sozlamalar.
5. Lidlar, statuslar va navbat.
6. Qo‘ng‘iroq sikli.
7. OnlinePBX, AI va AmoCRM.
8. Smenalar, tariflar, lokalizatsiya va Landing.
9. End-to-end va ekspluatatsion keyslar.
10. Tuzatishlarni qayta tekshirish va ta’sirlangan regress.

Login yoki kompaniyalar izolyatsiyasi buzilgan bo‘lsa, keyingi barcha
to‘plamni bajarishning ma’nosi yo‘q: avval bloklovchi nuqson ro‘yxatdan
o‘tkaziladi va davom ettirish bo‘yicha qaror qabul qilinadi.

### Smoke, regress va exploratory tekshiruv

**Smoke** «versiya batafsil testlashga umuman yaroqlimi?» degan savolga javob
beradi. U qisqa bo‘lib, har bir deploy’dan keyin bajariladi.

**Regress** «o‘zgarish avval ishlagan narsani buzmadimi?» degan savolga javob
beradi. U ta’sirlangan modullar va xatarlar bo‘yicha tanlanadi, reliz oldidan
esa to‘liq majburiy to‘plamgacha kengaytiriladi.

**Exploratory tekshiruv** test-keyslarni to‘ldiradi, ammo almashtirmaydi. Unga
vaqt chegarasi va maqsad beriladi, masalan: «ikki tab ochilganda navbat
xatti-harakatini 30 daqiqa o‘rganish». Barcha yangi kuzatuvlar qayd etiladi.

### Keysni qachon to‘xtatish kerak

- boshqa kompaniya ma’lumotlari ehtimoliy oshkor bo‘ldi;
- harakat haqiqiy mijozga borishi mumkin;
- keyingi qadam destruktiv va kelishilmagan;
- haqiqiy holat endi precondition’larga mos kelmaydi;
- himoyalangan saqlash joyida yo‘q sir talab qilinadi;
- kutilgan natija qarama-qarshi;
- bitta nuqson keyingi qadamlar natijasini ishonchsiz qiladi.

Izohda oxirgi bajarilgan qadam raqamini va to‘xtash sababini ko‘rsating.
