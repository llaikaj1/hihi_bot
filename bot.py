import os
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp
from bs4 import BeautifulSoup
from keep_alive import keep_alive
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токены из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

if not TELEGRAM_BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("Необходимо установить переменные окружения TELEGRAM_BOT_TOKEN и CHANNEL_ID")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
}

async def get_random_joke():
    try:
        print("Попытка получить анекдот...")
        url = 'https://www.anekdot.ru/random/anekdot/'
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    joke_div = soup.find('div', class_='text')
                    if joke_div and joke_div.text.strip():
                        return joke_div.text.strip()
        return None
    except Exception as e:
        print(f"Ошибка при получении анекдота: {str(e)}")
        return None

async def send_joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        joke = await get_random_joke()
        if joke:
            await update.message.reply_text(f"Анекдот:\n\n{joke}")
        else:
            await update.message.reply_text("Извините, не удалось получить анекдот.")
    except Exception as e:
        print(f"Ошибка при отправке анекдота: {str(e)}")
        await update.message.reply_text("Произошла ошибка при отправке анекдота.")

async def send_channel_joke():
    try:
        async with Bot(token=TELEGRAM_BOT_TOKEN) as bot:
            joke = await get_random_joke()
            if joke:
                await bot.send_message(chat_id=CHANNEL_ID, text=f"Анекдот дня:\n\n{joke}")
                print("Анекдот отправлен в канал")
            else:
                print("Не удалось получить анекдот для канала")
    except Exception as e:
        print(f"Ошибка при отправке в канал: {str(e)}")

async def main():
    try:
        # Запускаем веб-сервер для поддержания работы бота
        keep_alive()
        
        # Создаем приложение
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Добавляем обработчик команды /joke
        app.add_handler(CommandHandler("joke", send_joke_command))
        
        # Запускаем бота
        await app.initialize()
        await app.start()
        
        # Запускаем периодическую отправку анекдотов
        while True:
            await send_channel_joke()
            await asyncio.sleep(24 * 60 * 60)  # Ждем 24 часа
            
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        
if __name__ == "__main__":
    print("Бот запущен")
    asyncio.run(main())