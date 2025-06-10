import os
import pandas as pd
from telegram import Message


async def get_eda_analysis(message: Message):
    csv_path = os.path.join("data", "data.csv")

    if not os.path.exists(csv_path):
        await message.reply_text(
            "❌ CSV файл не найден. Пожалуйста, сначала загрузите данные."
        )
        return

    try:
        df = pd.read_csv(csv_path, sep=",", engine="python")

        if "Цена" not in df.columns:
            await message.reply_text("❌ Колонка 'Цена' не найдена в CSV файле.")
            return

        try:
            desc = df.describe().to_dict()
        except Exception:
            desc = {}

        report = "📊 **EDA Анализ данных**\n\n"
        report += f"📈 Размер данных: {df.shape[0]} строк, {df.shape[1]} колонок\n\n"
        report += f"📋 Колонки: {', '.join(list(df.columns))}\n\n"

        if desc:
            report += "📊 **Статистика по числовым колонкам:**\n"
            for col in desc:
                report += f"\n**{col}**\n"
                report += f"├ Количество: {desc[col].get('count', 0):.0f}\n"
                report += f"├ Среднее: {desc[col].get('mean', 0):.3f}\n"
                report += f"├ Станд.откл.: {desc[col].get('std', 0):.3f}\n"
                report += f"├ Минимум: {desc[col].get('min', 0):.3f}\n"
                report += f"├ 25%: {desc[col].get('25%', 0):.3f}\n"
                report += f"├ Медиана: {desc[col].get('50%', 0):.3f}\n"
                report += f"├ 75%: {desc[col].get('75%', 0):.3f}\n"
                report += f"└ Максимум: {desc[col].get('max', 0):.3f}\n"

        missing = df.isnull().sum()
        if missing.sum() > 0:
            report += "\n⚠️ **Пропущенные значения:**\n"
            for col, count in missing[missing > 0].items():
                report += f"• {col}: {count} ({count/len(df)*100:.1f}%)\n"

        if len(report) > 4096:
            for i in range(0, len(report), 4096):
                await message.reply_text(report[i : i + 4096], parse_mode="Markdown")
        else:
            await message.reply_text(report, parse_mode="Markdown")

    except Exception as e:
        await message.reply_text(f"❌ Ошибка при анализе данных: {str(e)}")
