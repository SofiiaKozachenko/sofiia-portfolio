# SOFIIA KOZACHENKO — PORTFOLIO V7

## Що змінилося

Тепер **відвідувач не повинен нічого встановлювати, імпортувати або відкривати на Behance**. Автоматичне завантаження презентацій відбувається на **етапі публікації сайту**. Проєкт зберігає оригінальну довгу HTML-презентацію кожного кейсу з локальними зображеннями та послідовністю блоків, у якій його опубліковано. Обкладинки імпортуються з Behance і зберігаються локально.

Головна сторінка з авторським 3D-персонажем та розширеним About/Experience збережена з V6; **єдина гарнітура Unbounded** підтримує українську та англійську. Кейси відкриваються всередині сайту. Презентації **не переверстуються** під єдиний шаблон.

## Головне: один раз підключити публікацію

1. Створи **публічний або приватний GitHub-репозиторій** із файлами цього архіву, задай основну гілку `main`.
2. Відкрий у ньому **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Запусти вкладку **Actions → Publish original Behance case studies → Run workflow**. Це перший запуск: у хмарі завантажаться п'ять кейсів і обкладинок та опублікується сайт.
4. Надалі workflow сам запускається при кожній зміні коду та **щодня** за розкладом. Не потрібно вручну качати кейси на комп’ютер. Відвідувач отримує готові сторінки без API, Figma, налаштувань і додаткових дій.

Перша публікація не є автоматичною з цього ZIP: потрібен GitHub-репозиторій із налаштованим Pages. Якщо Behance обмежує завантаження, збірка зупиниться і попередня успішно опублікована версія залишиться онлайн.

## Нові кейси

У `content/sources.json` можна додати свій публічний Behance-URL. Автопошук нових кейсів із профілю також є вбудованим як **best effort** і перевіряє дані авторства; можливість залежить від розмітки Behance. Гарантований спосіб додати новий кейс — вписати його URL до `additional`; після цього він з'явиться на сайті автоматично після наступної збірки. **Відвідувач ніколи цього не робить.**

Приклад:
```json
{
  "profile": "https://www.behance.net/sofiiakozachenko",
  "additional": [
    {"slug": "another-project", "url": "https://www.behance.net/gallery/123456789/Another-Project", "title": "Another Project", "category": "branding"}
  ]
}
```

## Що із якістю

- Презентації зберігаються в найвищій **публічно доступній** якості, яку знайде `behance-dl==0.3.0`; оригінали, доступні лише власниці в Adobe, не гарантуються.
- Для обкладинок імпортер перевіряє доступні варіанти CDN і обирає найбільший справжній файл (у збірці Pillow).
- Внутрішня презентація використовує автономний HTML, який повертає інструмент, тому текст і блоки йдуть у порядку Behance; можливі відмінності у відео й сторонніх інтерактивних вбудовуваннях.
- **Bean Road** імпортується безпосередньо з опублікованого https://www.behance.net/gallery/227566159/Coffee-shop-Bean-Road, а не збирається вручну з окремих Figma-постів.

## Ручне тестування на Mac (не потрібно відвідувачу)

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-sync.txt
.venv/bin/python scripts/build_site.py
.venv/bin/python -m http.server 8765
```
Відкрий `http://127.0.0.1:8765`. `python scripts/build_site.py --check-only` перевіряє, що всі кейси та обкладинки реально завантажені. Скрипт зупиняє публікацію, якщо якоїсь презентації бракує.

## Структура

- `.github/workflows/publish.yml` — автоматична синхронізація та публікація через GitHub Pages.
- `scripts/build_site.py` — синхронізація, перевірка якості й доступності сторінок.
- `scripts/stage_site.py` — створює чисту продакшен-збірку `dist/` без вихідних Python-скриптів.
- `scripts/import_behance.py` — завантажує презентації із Behance, зберігаючи кожен модуль.
- `content/sources.json` — джерела початкових і майбутніх кейсів.
- `content/behance-imports.js` — створюється під час збірки з реальними локальними шляхами.
- `assets/behance/` і `assets/covers/` — створюються під час збірки; в архіві їх ще немає, бо тут заблоковано мережеве завантаження Behance.
- `sanity/` — попередній каркас CMS, не потрібний для автоматичної публікації із Behance.

## Поточний стан

**Цей ZIP містить робочий код автоматичної збірки, а не вже опубліковані галереї.** У поточному середовищі немає мережевого доступу до Behance CDN, тому я не можу чесно назвати наповненим онлайн-сайтом до першого запуску синхронізації в GitHub Actions. Не відкривай `index.html` локально як остаточну перевірку кейсів: відкривай опубліковану збірку після успішної синхронізації.


## Performance and video (V8)

The deployment now generates 960px / 1920px / 2880px responsive WebP images (quality 92)
from original Behance gallery files, retaining the original full-resolution PNGs for
click-to-zoom. Gallery images are loaded lazily in a native page layout (no giant iframe),
while the first image loads immediately. Extra descriptions and project subtitles are not
added to the case itself. Bean Road's original Vimeo player URL, including the unlisted
video hash, is embedded responsively with native Vimeo playback controls. Playback depends
on Vimeo connectivity and the video owner's external embedding settings.

The workflow prepares these variants automatically after fetching Behance content. If a
required image or Bean Road video reference is absent, publishing is blocked.
