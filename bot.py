import os

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


BOT_TOKEN = _require_env("BOT_TOKEN")
WEBAPP_URL = _require_env("WEBAPP_URL")


# /start
async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            text="Открыть",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать в MeWe! 🎉",
        reply_markup=reply_markup
    )


# menu button
async def set_menu(app: Application):
    webapp_button = MenuButtonWebApp(
        text="Открыть",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    await app.bot.set_chat_menu_button(menu_button=webapp_button)


# hint
async def fallback_hint(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Открой MeWe командой /start 😊")


def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(set_menu)
        .build()
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(~filters.COMMAND, fallback_hint))
    app.run_polling()
    
if __name__ == '__main__':
    main()