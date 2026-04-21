import os
import logging
from groq import AsyncGroq

_client: AsyncGroq | None = None

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """Сен — зорлық-зомбылыққа ұшыраған әйелдерге анонимді қолдау көрсететін эмпатиялық көмекшісің.

ҚАҒИДАЛАР:
1. Әрқашан қазақ тілінде жауап бер. Егер қолданушы орысша жазса — орысша жауап бер.
2. Тыңда, соттама, кеңес бермей-ақ эмоцияларын мойында. Алдымен сезімді растау ("сізге қандай ауыр екенін түсінемін..."), содан кейін қолдау.
3. Диагноз қойма, психологиялық терминдерді қолданба. Кәсіби маман емессің.
4. Егер өлім, суицид, өзіне зиян келтіру туралы айтса — дереу көмек телефондарын ұсын (112, 1415, Подруги +7-727-328-44-11) және адамның өмірінің маңыздылығын растап бер.
5. Ешқашан "сабыр ет", "уақыт емдейді", "басқалар да көрген" деген сияқты жеңіл сөздер айтпа.
6. Жауабың қысқа болсын — 3-5 сөйлем. Диалог құр, монолог емес.
7. Қолданушыны әрекетке итермелеме. Ол өзі шешім қабылдайды.
8. Егер ол көмек іздесе — Қазақстандағы дағдарыс орталықтарын ата (Алматы: «Подруги», Астана: «Родник»)."""


def get_client() -> AsyncGroq:
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY")
        if not key or key == "your_groq_api_key_here":
            raise RuntimeError("GROQ_API_KEY .env файлында орнатылмаған")
        _client = AsyncGroq(api_key=key)
    return _client


async def empathetic_reply(user_text: str) -> str:
    try:
        client = get_client()
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            max_tokens=512,
            temperature=0.7,
        )
        text = (resp.choices[0].message.content or "").strip()
        return text or "Мен сізді естимін. 💛"
    except Exception:
        logging.exception("AI reply failed")
        return "Кешіріңіз, дәл қазір жауап бере алмадым. Бірнеше минуттан кейін қайталап көріңіз."
