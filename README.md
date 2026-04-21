# 🌸 Anonymous Support Bot (Анонимді қолдау)

Telegram-бот для анонимного приёма сообщений от женщин о случаях насилия.
AI-помощник (Claude Haiku 4.5) + веб-админка. Интерфейс на казахском.

## Стек

- **Python 3.13**
- **aiogram 3.13** — Telegram bot
- **FastAPI + Jinja2** — админка
- **SQLite (aiosqlite)** + SQLAlchemy
- **Google Gemini 2.0 Flash** — эмпатичный AI-помощник (бесплатный tier)

## Структура

```
anon-bot/
├── bot/              # Telegram бот
│   ├── main.py
│   ├── handlers/     # /start, /send, AI, /delete_my_data
│   ├── services/     # Claude, crisis detector, rate limit
│   ├── texts.py      # все тексты на каз
│   └── keyboards.py
├── admin/            # Web админка
│   ├── main.py       # FastAPI
│   ├── templates/    # Jinja2
│   └── static/
├── shared/           # БД и модели (общие)
│   ├── db.py
│   └── models.py
└── data/anon.db      # SQLite
```

## Установка

```bash
cd ~/Projects/anon-bot
python3.13 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
# открой .env и впиши BOT_TOKEN, ANTHROPIC_API_KEY, ADMIN_PASSWORD
```

### Получение ключей

1. **BOT_TOKEN** — напиши [@BotFather](https://t.me/BotFather) → `/newbot` → получи токен
2. **GEMINI_API_KEY** — https://aistudio.google.com/app/apikey → Create API key (бесплатно)
3. **ADMIN_PASSWORD** — придумай сам (используется для входа в админку)
4. **SESSION_SECRET** — случайная строка, например `python -c "import secrets; print(secrets.token_hex(32))"`

## Запуск

**Терминал 1 — бот:**
```bash
./venv/bin/python -m bot.main
```

**Терминал 2 — админка:**
```bash
./venv/bin/uvicorn admin.main:app --host 127.0.0.1 --port 8000
```

Админка: http://127.0.0.1:8000/login

## Фичи

- ✅ Полная анонимность — не хранятся username, только hash(chat_id)
- ✅ 5 категорий насилия (физ / психол / сексуал / семейное / другое)
- ✅ Детектор кризисных слов → мгновенно выдаёт КЗ хотлайны (112, 1415, Подруги)
- ✅ AI-помощник на Google Gemini 2.0 Flash (бесплатный)
- ✅ Rate limit (5 сообщений / минуту)
- ✅ Команда `/delete_my_data` — удаление всех своих сообщений
- ✅ Админ отвечает анонимно через веб-панель → юзер получает в боте
- ✅ Фильтры по статусу и категории, счётчики

## Хотлайны Казахстан

- **112** — единая экстренная
- **150** — Дети в беде
- **1415** — насилие в семье
- **+7 (727) 328-44-11** — «Подруги» (Алматы)
