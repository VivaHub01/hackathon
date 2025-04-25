import os
import openpyxl
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, BotCommand
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler,
                          ConversationHandler, ContextTypes, MessageHandler, filters)
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

# Состояния для расчёта 6 знаков: AA1231
(STEP_1, STEP_2, STEP_3, STEP_4, STEP_5, STEP_6, SHOW_RESULT) = range(7)

# Путь к Excel-файлу с разбаловкой
EXCEL_PATH = "Сетка анализа здания (1).xlsx"

# Загрузка данных из Excel (будет дорабатываться)
def load_scoring_data():
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    data = {}
    # пример: data['period'] = {'Новостройки': 'A', ...}
    # заглушка
    return data

data_from_excel = load_scoring_data()

# Стартовое меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Рассчитать по системе AA1231", callback_data="start_calc")],
        [InlineKeyboardButton("Поддержка", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)
    return ConversationHandler.END

# Обработка поддержки
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("📞 Поддержка: support@example.com")

# Начало расчёта
async def start_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.callback_query.edit_message_text("1️⃣ Введите период постройки здания:")
    return STEP_1

# Обработчики шагов (будут дорабатываться под варианты)
async def handle_step_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['step_1'] = update.message.text
    await update.message.reply_text("2️⃣ Введите материал стен:")
    return STEP_2

async def handle_step_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['step_2'] = update.message.text
    await update.message.reply_text("3️⃣ Введите этажность, наличие лифтов и др. параметры:")
    return STEP_3

async def handle_step_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['step_3'] = update.message.text
    await update.message.reply_text("4️⃣ Введите параметры техобслуживания:")
    return STEP_4

async def handle_step_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['step_4'] = update.message.text
    await update.message.reply_text("5️⃣ Введите параметры хоз.обслуживания:")
    return STEP_5

async def handle_step_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['step_5'] = update.message.text
    await update.message.reply_text("6️⃣ Введите периодичные затраты:")
    return STEP_6

async def handle_step_6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['step_6'] = update.message.text
    # здесь будет вычисление кода AA1231
    code = "AA1231"  # заглушка
    await update.message.reply_text(f"✅ Результат: {code}")
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_calc, pattern="^start_calc$")],
        states={
            STEP_1: [CommandHandler("start", start), MessageHandler(filters.TEXT & ~filters.COMMAND, handle_step_1)],
            STEP_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_step_2)],
            STEP_3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_step_3)],
            STEP_4: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_step_4)],
            STEP_5: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_step_5)],
            STEP_6: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_step_6)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(support, pattern="^support$"))

    async def set_commands(_: Application):
        await app.bot.set_my_commands([BotCommand("start", "Главное меню")])

    app.post_init = set_commands
    app.run_polling()

if __name__ == "__main__":
    main()
