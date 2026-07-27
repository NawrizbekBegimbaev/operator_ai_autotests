# Окружения, доступы и безопасность

[← Продукт и термины](01-product-and-terms.md) · [Главная](../README.md) ·
[Далее: тестовые данные →](03-test-data.md)

## Главное правило

| Окружение | Разрешено | Запрещено |
| --- | --- | --- |
| staging/test | Создавать, изменять и удалять согласованные тестовые данные; выполнять ручные и автоматические проверки | Звонить реальным клиентам, использовать реальные секреты без необходимости |
| local | Исследовать интерфейс и API на локальных данных | Считать результат локального прогона достаточным для релиза |
| production | Пассивно открыть страницу, проверить доступность, наблюдать метрики по согласованию | Создавать, изменять, удалять данные, воспроизводить дефекты, запускать автотесты или нагрузку |

Доступ к production — это возможность разобрать инцидент, а не разрешение
тестировать на клиентах.

## Что должно быть выдано до начала прогона

Адреса, логины, токены и ключи хранятся только в `.env` или защищённом
хранилище команды. В Wiki и тест-кейсы записываются названия переменных, но не
значения.

- URL Admin, Landing и API на staging;
- аккаунты Super-admin, ROP и Operator;
- две изолированные тестовые компании для проверок tenant isolation;
- минимум два оператора для проверки конкуренции;
- тестовая AmoCRM с отдельной воронкой;
- тестовая OnlinePBX, включённый внутренний номер и разрешённые телефоны;
- доступ к `/docs`, `/openapi.yaml`, `/healthz` и `/readyz`;
- безопасный просмотр логов staging;
- информация о версии front/back/landing, выложенной на стенд;
- контакт ответственного разработчика или DevOps на случай блокера.

Если чего-то нет, укажи это как блокер. Не заменяй отсутствующий тестовый
ресурс реальным аккаунтом клиента.

## Preflight перед каждым прогоном

Preflight — как проверка приборов перед взлётом. Она не доказывает, что весь
самолёт исправен, но не даёт потратить часы на тестирование заведомо
неработающего стенда.

- [ ] Убедись, что открыт staging, а не production.
- [ ] Запиши дату, время и проверяемую версию/commit SHA.
- [ ] `GET /healthz` отвечает успешно.
- [ ] `GET /readyz` подтверждает готовность приложения.
- [ ] Страница входа и основные JS/CSS-ресурсы загружаются без 404.
- [ ] Три роли могут войти или известен согласованный блокер.
- [ ] Тестовая AmoCRM доступна и выбрана правильная воронка.
- [ ] Тестовая OnlinePBX активна, внутренний номер включён.
- [ ] Используемый телефон подтверждён как тестовый.
- [ ] Известно, какие данные будут созданы и как их удалить.
- [ ] Время и часовой пояс стенда понятны для проверок очереди и смен.
- [ ] Нет объявленного инцидента или параллельных работ на окружении.

Не ставь функциональным кейсам `Failed`, если preflight показал, что всё
окружение недоступно. Это `Blocked` с описанием общей причины.

## Правила работы с секретами

Секретом считаются пароль, access/refresh token, API key, webhook token,
client secret, закрытый URL, cookie сессии и данные реального клиента.

Обязательные правила:

1. Не вставляй секреты в Excel, Markdown, баг-репорт или чат.
2. Перед скриншотом закрой вкладки Application/Cookies и замажь заголовок
   `Authorization`.
3. В request/response оставляй структуру, но заменяй значение на
   `<скрыто>`.
4. Не прикладывай полный `.env`.
5. Если секрет попал в лог или вложение, останови распространение,
   сообщи ответственным и потребуй ротацию.
6. Не используй один пароль для тестовой и личной учётной записи.

## Работа с внешними системами

### AmoCRM

- Проверяй ID аккаунта, воронки и лида до изменения.
- Используй только тестовую воронку и заранее созданные тестовые статусы.
- После кейса сравни состояние и в Operator AI, и в AmoCRM.
- Не удаляй всю воронку или группу полей ради одного негативного теста.

### OnlinePBX

- Перед звонком вслух или в комментарии зафиксируй тестовый номер.
- Не перебирай все номера контакта, если среди них может быть реальный.
- Массовые вебхуки, повтор событий и нагрузка выполняются только по
  согласованному сценарию.
- Не меняй общую конфигурацию клиента ради локального теста.

### Gemini

- Реальные записи клиентов не используются как учебные данные.
- Для повторяемого теста готовь согласованное тестовое аудио.
- Не запускай многократную дорогую обработку без необходимости.
- При ошибке проверяй, что ключ не попал в лог.

## Если случайно открыли production

1. Ничего не нажимай в формах изменения.
2. Не пытайся «быстро проверить один шаг».
3. Закрой вкладку или перейди на staging через сохранённую безопасную ссылку.
4. Если изменение уже произошло, не скрывай его и не исправляй наугад.
5. Зафиксируй время, пользователя, сущность и действие.
6. Немедленно сообщи ответственному QA и владельцу системы.

## Действия, требующие отдельного согласования

- нагрузочный или стресс-тест;
- временная остановка API или интеграции;
- перезапуск Backend;
- изменение системного времени;
- удаление больших объёмов данных;
- проверка восстановления из резервной копии;
- тест CORS с реальными credentials;
- массовая отправка вебхуков;
- попытка повысить права или получить данные другой компании;
- любой тест, способный вызвать реальные звонки.

---

## O‘zbekcha versiya

[← Mahsulot va atamalar](01-product-and-terms.md) · [Asosiy sahifa](../README.md) ·
[Keyingi: test ma’lumotlari →](03-test-data.md)

### Asosiy qoida

| Muhit | Ruxsat etiladi | Taqiqlanadi |
| --- | --- | --- |
| staging/test | Kelishilgan test ma’lumotlarini yaratish, o‘zgartirish va o‘chirish; qo‘lda va avtomatik tekshiruvlarni bajarish | Haqiqiy mijozlarga qo‘ng‘iroq qilish, zaruratsiz haqiqiy sirlardan foydalanish |
| local | Mahalliy ma’lumotlarda interfeys va API’ni o‘rganish | Lokal test natijasini reliz uchun yetarli deb hisoblash |
| production | Sahifani passiv ochish, mavjudligini tekshirish, kelishilgan holda metrikalarni kuzatish | Ma’lumot yaratish, o‘zgartirish yoki o‘chirish, nuqsonni takrorlash, avtotest yoki yuklama ishga tushirish |

Production’ga kirish — hodisani tahlil qilish imkoniyati, mijozlarda test
o‘tkazishga ruxsat emas.

### Test boshlanishidan oldin berilishi kerak bo‘lgan narsalar

Manzillar, loginlar, tokenlar va kalitlar faqat `.env` yoki jamoaning
himoyalangan saqlash joyida turadi. Wiki va test-keyslarda qiymatlar emas,
faqat o‘zgaruvchi nomlari yoziladi.

- staging’dagi Admin, Landing va API URL’lari;
- Super-admin, ROP va Operator akkauntlari;
- tenant isolation tekshiruvlari uchun ikkita ajratilgan test kompaniya;
- parallel ishlashni tekshirish uchun kamida ikki operator;
- alohida voronkaga ega test AmoCRM;
- test OnlinePBX, yoqilgan ichki raqam va ruxsat berilgan telefonlar;
- `/docs`, `/openapi.yaml`, `/healthz` va `/readyz` ga kirish;
- staging loglarini xavfsiz ko‘rish;
- stendga joylangan front/back/landing versiyasi haqida ma’lumot;
- bloklovchi holat uchun mas’ul dasturchi yoki DevOps kontakti.

Biror narsa yetishmasa, uni bloklovchi sabab sifatida ko‘rsating. Yetishmagan
test resursini haqiqiy mijoz akkaunti bilan almashtirmang.

### Har bir testdan oldingi preflight

Preflight — parvozdan oldingi asboblar tekshiruviga o‘xshaydi. U butun tizim
sozligini isbotlamaydi, ammo aniq ishlamayotgan stendni soatlab test qilishga
yo‘l qo‘ymaydi.

- [ ] Staging ochilganiga, production emasligiga ishonch hosil qiling.
- [ ] Sana, vaqt va tekshirilayotgan versiya/commit SHA’ni yozing.
- [ ] `GET /healthz` muvaffaqiyatli javob beradi.
- [ ] `GET /readyz` ilova tayyorligini tasdiqlaydi.
- [ ] Login sahifasi va asosiy JS/CSS resurslari 404’siz yuklanadi.
- [ ] Uchala rol kira oladi yoki kelishilgan bloklovchi sabab ma’lum.
- [ ] Test AmoCRM mavjud va to‘g‘ri voronka tanlangan.
- [ ] Test OnlinePBX faol, ichki raqam yoqilgan.
- [ ] Ishlatilayotgan telefon test raqami sifatida tasdiqlangan.
- [ ] Qanday ma’lumot yaratilishi va qanday o‘chirilishi ma’lum.
- [ ] Navbat va smenalarni tekshirish uchun stend vaqti hamda vaqt zonasi
  tushunarli.
- [ ] Muhitda e’lon qilingan hodisa yoki parallel ishlar yo‘q.

Preflight butun muhit ishlamasligini ko‘rsatsa, funksional keyslarga `Failed`
qo‘ymang. Bu umumiy sabab tavsifi bilan `Blocked` bo‘ladi.

### Sirlar bilan ishlash qoidalari

Parol, access/refresh token, API key, webhook token, client secret, yopiq URL,
sessiya cookie’si va haqiqiy mijoz ma’lumotlari sir hisoblanadi.

Majburiy qoidalar:

1. Sirlarni Excel, Markdown, bag-report yoki chatga joylamang.
2. Skrinshotdan oldin Application/Cookies oynalarini yoping va
   `Authorization` sarlavhasini yashiring.
3. Request/response tuzilishini qoldiring, ammo qiymatni `<yashirilgan>` bilan
   almashtiring.
4. To‘liq `.env` faylini biriktirmang.
5. Sir log yoki ilovaga tushib qolsa, tarqalishni to‘xtating, mas’ullarga
   xabar bering va rotatsiya talab qiling.
6. Test va shaxsiy akkaunt uchun bitta paroldan foydalanmang.

### Tashqi tizimlar bilan ishlash

#### AmoCRM

- O‘zgartirishdan oldin akkaunt, voronka va lid ID’sini tekshiring.
- Faqat test voronkasi va oldindan yaratilgan test statuslaridan foydalaning.
- Keysdan keyin Operator AI va AmoCRM holatini solishtiring.
- Bitta negativ test uchun butun voronka yoki maydonlar guruhini o‘chirmang.

#### OnlinePBX

- Qo‘ng‘iroqdan oldin test raqamini ovoz chiqarib yoki izohda qayd eting.
- Kontakt raqamlari orasida haqiqiy raqam bo‘lishi mumkin bo‘lsa, ularning
  barchasini ketma-ket sinamang.
- Ommaviy webhook, hodisa takrori va yuklama faqat kelishilgan ssenariy
  bo‘yicha bajariladi.
- Lokal test uchun mijozning umumiy konfiguratsiyasini o‘zgartirmang.

#### Gemini

- Haqiqiy mijoz suhbatlari o‘quv ma’lumoti sifatida ishlatilmaydi.
- Takrorlanadigan test uchun kelishilgan test audiosini tayyorlang.
- Zaruratsiz ko‘p martalik qimmat ishlov berishni boshlamang.
- Xato yuz bersa, kalit logga tushmaganini tekshiring.

### Production tasodifan ochilsa

1. O‘zgartirish formalarida hech narsani bosmang.
2. «Faqat bitta qadamni tez tekshirish»ga urinmang.
3. Varaqni yoping yoki saqlangan xavfsiz havola orqali staging’ga o‘ting.
4. O‘zgarish allaqachon sodir bo‘lgan bo‘lsa, uni yashirmang va taxmin bilan
   tuzatmang.
5. Vaqt, foydalanuvchi, obyekt va harakatni qayd eting.
6. Darhol mas’ul QA va tizim egasiga xabar bering.

### Alohida kelishuv talab qiladigan harakatlar

- yuklama yoki stress testi;
- API yoki integratsiyani vaqtincha to‘xtatish;
- Backend’ni qayta ishga tushirish;
- tizim vaqtini o‘zgartirish;
- katta hajmdagi ma’lumotlarni o‘chirish;
- zaxira nusxadan tiklashni tekshirish;
- haqiqiy credentials bilan CORS testi;
- webhooklarni ommaviy yuborish;
- huquqni oshirish yoki boshqa kompaniya ma’lumotini olishga urinish;
- haqiqiy qo‘ng‘iroqlarni yuzaga keltirishi mumkin bo‘lgan har qanday test.
