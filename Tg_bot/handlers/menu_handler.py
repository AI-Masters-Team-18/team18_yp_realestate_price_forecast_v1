from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! 👋")
    await show_main_menu(update)


async def show_main_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("📊 Загрузить данные", callback_data="upload_data")],
        [InlineKeyboardButton("📈 Получить EDA", callback_data="get_eda")],
        [InlineKeyboardButton("🤖 Обучить модель", callback_data="train_model")],
        [
            InlineKeyboardButton(
                "💰 Предсказать стоимость", callback_data="predict_price"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text(
            "Выберите действие:", reply_markup=reply_markup
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.upload_handler import WAITING_CSV
    from handlers.predict_handler import ASKING_DISTANCE, user_data
    from handlers.eda_handler import get_eda_analysis
    from handlers.train_handler import train_model

    query = update.callback_query
    await query.answer()

    if query.data == "upload_data":
        await query.message.reply_text("Пожалуйста, отправьте CSV файл с данными.")
        return WAITING_CSV

    elif query.data == "get_eda":
        await get_eda_analysis(query.message)
        await show_main_menu(update)

    elif query.data == "train_model":
        await train_model(query.message)
        await show_main_menu(update)

    elif query.data == "predict_price":
        user_id = query.from_user.id
        user_data[user_id] = {}
        await query.message.reply_text(
            "Начинаем процесс предсказания стоимости.\n\n"
            "Введите расстояние квартиры до центра (в км).\n"
            "Введите 0 для пропуска."
        )
        return ASKING_DISTANCE
