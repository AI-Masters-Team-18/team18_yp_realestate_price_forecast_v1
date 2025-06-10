import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler
from handlers.menu_handler import start, show_main_menu, button_callback
from handlers.upload_handler import handle_csv, WAITING_CSV
from handlers.predict_handler import (
    ask_distance,
    ask_rooms,
    ask_area,
    ask_floor,
    ask_repair,
    ask_year,
    ask_ceiling,
    ask_walls,
    ask_type,
    ask_station,
    ask_time,
    ASKING_DISTANCE,
    ASKING_ROOMS,
    ASKING_AREA,
    ASKING_FLOOR,
    ASKING_REPAIR,
    ASKING_YEAR,
    ASKING_CEILING,
    ASKING_WALLS,
    ASKING_TYPE,
    ASKING_STATION,
    ASKING_TIME,
)
from telegram.ext import MessageHandler, filters, CallbackQueryHandler
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

for folder in ["data", "model"]:
    if not os.path.exists(folder):
        os.makedirs(folder)


async def cancel(update: Update, context):
    from handlers.predict_handler import user_data

    user_id = update.message.from_user.id
    if user_id in user_data:
        del user_data[user_id]

    await update.message.reply_text("Операция отменена.")
    await show_main_menu(update)
    return ConversationHandler.END


def main():
    TOKEN = ""

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback)],
        states={
            WAITING_CSV: [MessageHandler(filters.Document.ALL, handle_csv)],
            ASKING_DISTANCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_distance)
            ],
            ASKING_ROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_rooms)],
            ASKING_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_area)],
            ASKING_FLOOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_floor)],
            ASKING_REPAIR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_repair)
            ],
            ASKING_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_year)],
            ASKING_CEILING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ceiling)
            ],
            ASKING_WALLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_walls)],
            ASKING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_type)],
            ASKING_STATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_station)
            ],
            ASKING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_time)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
