import os
from typing import Any

from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    Update,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ExtBot,
    JobQueue,
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


# Тип приложения, которое собирает ApplicationBuilder() без своих настроек
type BotApplication = Application[
    ExtBot[None],
    ContextTypes.DEFAULT_TYPE,
    dict[Any, Any],
    dict[Any, Any],
    dict[Any, Any],
    JobQueue[ContextTypes.DEFAULT_TYPE],
]


# /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # effective_message: у отредактированного сообщения update.message — None
    message = update.effective_message
    if message is None:
        return

    keyboard = [[
        InlineKeyboardButton(
            text="Открыть",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(
        "Добро пожаловать в MeWe! 🎉",
        reply_markup=reply_markup
    )


# menu button
async def set_menu(app: BotApplication) -> None:
    webapp_button = MenuButtonWebApp(
        text="Открыть",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    await app.bot.set_chat_menu_button(menu_button=webapp_button)


# hint
async def fallback_hint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return

    await message.reply_text("Открой MeWe командой /start 😊")


def main() -> None:
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        # В типах python-telegram-bot параметр post_init — Application[Unknown, ...]
        .post_init(set_menu)  # pyright: ignore[reportUnknownMemberType]
        .build()
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(~filters.COMMAND, fallback_hint))
    app.run_polling()


if __name__ == '__main__':
    main()