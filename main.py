import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

def ask_gemini(prompt_text):
    if not GEMINI_API_KEY:
        return "Ошибка: Переменная GEMINI_API_KEY не найдена на сервере Render."

    # Очищаем ключ от возможных лишних кавычек и пробелов
    clean_key = GEMINI_API_KEY.strip().strip('"').strip("'")

    # Использование актуального эндпоинта Gemini 3.6 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={clean_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    response = requests.post(url, json=data, headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        try:
            return result['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "Ответ получен в некорректном формате."
    else:
        return f"Ошибка API ({response.status_code}): {response.text}"

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я твой ИИ-помощник, запущенный 24/7.")

@dp.message()
async def handle_ai(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(None, ask_gemini, message.text)
        await message.answer(answer)
    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке: {e}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
