import os
import logging

from typing import Callable, Dict, Awaitable, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main_menu_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Next lesson", callback_data="nextlesson"),
            InlineKeyboardButton("Weekly schedule", callback_data="schedule"),
        ],
        [
            InlineKeyboardButton("Last lessons per day", callback_data="lastlessons"),
            InlineKeyboardButton("Upcoming exams", callback_data="exams"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Back to menu", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def send_message_safe(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> None:
    """
    Send or edit a message safely depending on update content.
    Preference order:
      1. update came from callback query -> edit the callback message
      2. message exists -> reply to it
      3. effective_chat exists -> send a new message to that chat
      4. otherwise log and do nothing
    """
    if update.callback_query is not None:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        return

    if update.message is not None:
        await update.message.reply_text(text=text, reply_markup=reply_markup)
        return

    if update.effective_chat is not None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
        return

    logger.warning("send_message_safe: no callback_query, no message, no effective_chat in update: %s", update)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Welcome to the Edupage bot.\n\n"
        "Choose an action from the menu below:"
    )
    await send_message_safe(update, context, text=text, reply_markup=main_menu_markup())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message_safe(update, context, text="Available commands: /nextlesson, /schedule, /lastlessons, /exams", reply_markup=main_menu_markup())


async def cmd_nextlesson(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message_safe(update, context, text="Fetching next lesson...", reply_markup=main_menu_markup())
    await send_next_lesson_msg(update, context)


async def cmd_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message_safe(update, context, text="Fetching weekly schedule...", reply_markup=main_menu_markup())
    await send_weekly_schedule_msg(update, context)


async def cmd_lastlessons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message_safe(update, context, text="Fetching last lessons per day...", reply_markup=main_menu_markup())
    await send_last_lessons_msg(update, context)


async def cmd_exams(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message_safe(update, context, text="Fetching upcoming exams...", reply_markup=main_menu_markup())
    await send_upcoming_exams_msg(update, context)


async def send_next_lesson_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message_safe(update, context, "TODO", reply_markup=back_markup())


async def send_weekly_schedule_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message_safe(update, context, "TODO", reply_markup=back_markup())


async def send_last_lessons_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message_safe(update, context, "TODO", reply_markup=back_markup())


async def send_upcoming_exams_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_message_safe(update, context, "TODO", reply_markup=back_markup())


async def button_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    data = query.data or ""

    router: Dict[str, Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]] = {
        "menu": start_command,
        "nextlesson": send_next_lesson_msg,
        "schedule": send_weekly_schedule_msg,
        "lastlessons": send_last_lessons_msg,
        "exams": send_upcoming_exams_msg,
    }

    handler = router.get(data)
    if handler:
        await handler(update, context)
    else:
        await send_message_safe(update, context, text="Unknown action.", reply_markup=main_menu_markup())


def build_application(token: str):
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("nextlesson", cmd_nextlesson))
    app.add_handler(CommandHandler("schedule", cmd_schedule))
    app.add_handler(CommandHandler("lastlessons", cmd_lastlessons))
    app.add_handler(CommandHandler("exams", cmd_exams))

    app.add_handler(CallbackQueryHandler(button_callback_router))

    return app


def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN environment variable is not set. Exiting.")
        raise SystemExit("TELEGRAM_TOKEN environment variable is required")

    app = build_application(token)
    logger.info("Starting Edupage Telegram bot (polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()