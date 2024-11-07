from keep_alive import keep_alive
keep_alive()  # Запускаем веб-сервер

import os
import asyncio
from telegram.ext import Application, CommandHandler
from telegram import Bot
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

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

async def send_joke_command(update, context):
    try:
        joke = await get_random_joke()
        if joke:
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
            message = f"Анекдот ({current_time}):\n\n{joke}"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Извините, не удалось получить анекдот.")
    except Exception as e:
        print(f"Ошибка при отправке анекдота: {str(e)}")
        await update.message.reply_text("Произошла ошибка при отправке анекдота.")

async def scheduled_joke():
    try:
        async with Bot(token=TELEGRAM_BOT_TOKEN) as bot:
            joke = await get_random_joke()
            if joke:
                current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
                message = f"Анекдот дня ({current_time}):\n\n{joke}"
                await bot.send_message(chat_id=CHANNEL_ID, text=message)
                print("Сообщение успешно отправлено")
            else:
                print("Нет анекдота для отправки")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {str(e)}")

async def main():
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчик команды /joke
    application.add_handler(CommandHandler("joke", send_joke_command))
    
    # Запускаем бота
    await application.initialize()
    await application.start()
    
    # Запускаем периодическую отправку анекдотов
    while True:
        try:
            await scheduled_joke()
            # Ждем 24 часа
            await asyncio.sleep(24 * 60 * 60)
        except Exception as e:
            print(f"Ошибка в главном цикле: {str(e)}")
            await asyncio.sleep(300)

if __name__ == "__main__":
    print("Бот запущен")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")