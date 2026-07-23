import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных окружения! Добавьте его в настройках бота.")
