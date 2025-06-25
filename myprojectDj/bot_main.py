import logging
import os

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "http://localhost:8000/api/user-info/"  # Для продакшена заменить на реальный URL

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Используй /myinfo чтобы получить свои данные")


async def myinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        response = requests.get(
            API_URL,
            params={"telegram_id": str(user.id)},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            message = (
                f"👤 Имя пользователя: {data['username']}\n"
                f"📧 Email: {data['email']}\n"
                f"👨 Имя: {data['first_name']}\n"
                f"👪 Фамилия: {data['last_name']}\n"
                f"🆔 Telegram ID: {data['telegram_id']}\n"
                f"📱 Телефон: {data['phone']}"
            )
        elif response.status_code == 404:
            message = "❌ Пользователь не найден. Зарегистрируйтесь в системе!"
        else:
            message = "⚠️ Ошибка сервера. Попробуйте позже"

    except Exception as e:
        logger.error(f"API request failed: {e}")
        message = "🚫 Ошибка соединения с сервером"

    await update.message.reply_text(message)


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("myinfo", myinfo))

    application.run_polling()


if __name__ == "__main__":
    main()