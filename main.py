import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Вставьте ваши реальные ключи
TELEGRAM_BOT_TOKEN = "8966437564:AAG4lEatYIGPTAqNMDtBxPUQz5QogGQKP3k"
GEMINI_API_KEY = "AQ.Ab8RN6Jc0TsjUBDuk6LZaUVwNVFQNN-G2LlmEjrNg_ec2GkTtQ"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

def ask_gemini(prompt_text):
    """Запрос к Gemini API с правильной авторизацией через заголовки"""
    url = "f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Передаем ключ авторизации через спец-заголовок x-goog-api-key
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
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
            return "Ответ от нейросети получен в некорректном формате."
    else:
        return f"Ошибка API ({response.status_code}): {response.text}"

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я твой ИИ-помощник.")

@dp.message()
async def handle_ai(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(None, ask_gemini, message.text)
        await message.answer(answer)
    except Exception as e:
        await message.answer(f"Произошла ошибка при отправке: {e}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
