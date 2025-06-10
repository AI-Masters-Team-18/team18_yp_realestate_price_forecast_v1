import os
import pandas as pd
import joblib
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

(
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
) = range(11)

user_data = {}


async def ask_distance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        distance = float(text)
        user_data[user_id]["Расстояние до центра"] = distance if distance != 0 else None

        keyboard = [["0", "1", "2"], ["3", "4", "5+"], ["free", "Пропустить"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(reply_markup=reply_markup)
        return ASKING_ROOMS

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число или 0 для пропуска.")
        return ASKING_DISTANCE


async def ask_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "Пропустить":
        user_data[user_id]["Кол-во комнат"] = None
    else:
        user_data[user_id]["Кол-во комнат"] = text

    await update.message.reply_text(
        "Введите площадь квартиры (в кв.м).\n" "Введите 0 для пропуска.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASKING_AREA


async def ask_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        area = float(text)
        user_data[user_id]["Общая площадь"] = area if area != 0 else None

        await update.message.reply_text(
            "Введите желаемый этаж.\n" "Введите 0 для пропуска."
        )
        return ASKING_FLOOR

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число или 0 для пропуска.")
        return ASKING_AREA


async def ask_floor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        floor = int(text)
        user_data[user_id]["Этаж"] = floor if floor != 0 else None

        keyboard = [
            ["Нужен ремонт", "Без отделки"],
            ["Хороший", "Дизайнерский"],
            ["Евро", "Чистовая отделка"],
            ["Черновая отделка", "Предчистовая отделка"],
            ["Пропустить"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "Выберите тип ремонта:", reply_markup=reply_markup
        )
        return ASKING_REPAIR

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число или 0 для пропуска.")
        return ASKING_FLOOR


async def ask_repair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "Пропустить":
        user_data[user_id]["Ремонт"] = None
    else:
        user_data[user_id]["Ремонт"] = text

    await update.message.reply_text(
        "Введите желаемый год постройки.\n" "Введите 0 для пропуска.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASKING_YEAR


async def ask_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        year = int(text)
        user_data[user_id]["Год постройки"] = year if year != 0 else None

        await update.message.reply_text(
            "Введите желаемую высоту потолков (в метрах).\n" "Введите 0 для пропуска."
        )
        return ASKING_CEILING

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите год или 0 для пропуска.")
        return ASKING_YEAR


async def ask_ceiling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        ceiling = float(text)
        user_data[user_id]["Высота потолков"] = ceiling if ceiling != 0 else None

        keyboard = [
            ["монолит", "кирпич"],
            ["панель", "кирпич-монолит"],
            ["блок", "Пропустить"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "Выберите материал стен:", reply_markup=reply_markup
        )
        return ASKING_WALLS

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число или 0 для пропуска.")
        return ASKING_CEILING


async def ask_walls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "Пропустить":
        user_data[user_id]["Материал стен"] = None
    else:
        user_data[user_id]["Материал стен"] = text

    keyboard = [["квартира", "апартаменты"], ["Пропустить"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Выберите тип жилья:", reply_markup=reply_markup)
    return ASKING_TYPE


async def ask_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "Пропустить":
        user_data[user_id]["Тип жилья"] = None
    else:
        user_data[user_id]["Тип жилья"] = text

    await update.message.reply_text(
        "Введите название ближайшей станции метро.\n" "Введите 0 для пропуска.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASKING_STATION


async def ask_station(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "0":
        user_data[user_id]["Станция"] = None
    else:
        user_data[user_id]["Станция"] = text

    await update.message.reply_text(
        "Введите время до метро (в минутах).\n" "Введите 0 для пропуска."
    )
    return ASKING_TIME


async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        time = int(text)
        user_data[user_id]["Время"] = time if time != 0 else None

        model_path = os.path.join("model", "model.pkl")

        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)

                user_df = pd.DataFrame([user_data[user_id]])

                prediction = model.predict(user_df)[0]

                result = "📋 **Результаты предсказания:**\n\n"
                result += f"💰 **Предсказанная стоимость: {prediction:,.0f} руб.**\n\n"
                result += "📊 **Использованные параметры:**\n"

                for key, value in user_data[user_id].items():
                    if value is not None:
                        result += f"• {key}: {value}\n"

                await update.message.reply_text(result, parse_mode="Markdown")

            except Exception as e:
                result = "📋 Собранные данные:\n\n"
                for key, value in user_data[user_id].items():
                    if value is not None:
                        result += f"• {key}: {value}\n"

                result += f"\n⚠️ Не удалось сделать предсказание: {str(e)}"
                await update.message.reply_text(result)
        else:
            result = "📋 Собранные данные:\n\n"
            for key, value in user_data[user_id].items():
                if value is not None:
                    result += f"• {key}: {value}\n"

            result += "\n⚠️ Модель не обучена. Пожалуйста, сначала обучите модель."
            await update.message.reply_text(result)

        del user_data[user_id]

        from handlers.menu_handler import show_main_menu

        await show_main_menu(update)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число или 0 для пропуска.")
        return ASKING_TIME
