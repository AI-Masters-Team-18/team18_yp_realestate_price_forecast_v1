import os
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

WAITING_CSV = 0


async def handle_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document

        if not document:
            await update.message.reply_text("❌ Пожалуйста, отправьте документ.")
            return WAITING_CSV

        if document.mime_type == "text/csv" or document.file_name.endswith(".csv"):
            await update.message.reply_text("⏳ Загружаю файл...")

            file = await context.bot.get_file(document.file_id)

            if not os.path.exists("data"):
                os.makedirs("data")

            file_path = os.path.join("data", "data.csv")
            await file.download_to_drive(file_path)

            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                await update.message.reply_text(
                    f"✅ CSV файл успешно загружен!\n"
                    f"📁 Сохранен как: data.csv\n"
                    f"📊 Размер: {file_size:,} байт"
                )
            else:
                await update.message.reply_text("❌ Ошибка при сохранении файла.")

            from handlers.menu_handler import show_main_menu

            await show_main_menu(update)
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                f"❌ Неверный формат файла.\n"
                f"📄 Получен: {document.mime_type}\n"
                f"📋 Пожалуйста, отправьте файл в формате CSV."
            )
            return WAITING_CSV

    except Exception as e:
        logger.error(f"Ошибка при загрузке CSV: {e}")
        await update.message.reply_text(f"❌ Ошибка при загрузке файла: {str(e)}")

        from handlers.menu_handler import show_main_menu

        await show_main_menu(update)
        return ConversationHandler.END
