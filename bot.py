import os
import asyncio
from telegram import Bot
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup

# Получаем переменные окружения
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

async def send_joke():
    try:
        print("Начало отправки сообщения...")
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
    while True:  # Бесконечный цикл
        try:
            print("Начало выполнения main()")
            await send_joke()
            print("Завершение main()")
            # Ждем 24 часа перед следующей отправкой
            await asyncio.sleep(24 * 60 * 60)
        except Exception as e:
            print(f"Критическая ошибка: {str(e)}")
            # Ждем 5 минут перед повторной попыткой
            await asyncio.sleep(300)

if __name__ == "__main__":
    print("Скрипт запущен")
    asyncio.run(main())