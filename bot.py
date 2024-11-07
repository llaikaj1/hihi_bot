import requests
from bs4 import BeautifulSoup
from telegram.ext import Application
import schedule
import time
import asyncio
from datetime import datetime
import os

# Замените на свой токен бота
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# ID вашего канала (можно получить через @username_to_id_bot)
CHANNEL_ID = os.getenv('CHANNEL_ID')

async def get_random_joke():
    try:
        response = requests.get('https://www.anekdot.ru/random/anekdot/')
        soup = BeautifulSoup(response.text, 'html.parser')
        # Находим текст анекдота в div с классом 'text'
        joke = soup.find('div', class_='text').text.strip()
        return joke
    except Exception as e:
        print(f"Ошибка при получении анекдота: {e}")
        return None

async def send_joke():
    try:
        bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        joke = await get_random_joke()
        
        if joke:
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
            message = f"Анекдот дня ({current_time}):\n\n{joke}"
            
            async with bot:
                await bot.bot.send_message(chat_id=CHANNEL_ID, text=message)
            
            print(f"Анекдот успешно отправлен в {current_time}")
        else:
            print("Не удалось получить анекдот")
    except Exception as e:
        print(f"Ошибка при отправке анекдота: {e}")

def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Настраиваем расписание (например, каждый день в 12:00)
    schedule.every().day.at("12:00").do(lambda: asyncio.run(send_joke()))
    
    print("Бот запущен. Ожидание следующей отправки...")
    
    # Запускаем проверку расписания в отдельном потоке
    schedule_checker()