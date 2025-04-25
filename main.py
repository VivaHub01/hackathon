from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler, ConversationHandler
)
from telegram import BotCommand
from datetime import datetime
from dotenv import load_dotenv
import os
import asyncio

# Загружаем переменные окружения из .env
load_dotenv()

# Состояния для расчета стоимости
(
    CALC_START,
    CALC_PERIOD, CALC_WALL_MATERIAL, CALC_FLOORS, CALC_ELEVATOR, 
    CALC_GARBAGE_CHUTE, CALC_SMOKE_REMOVAL, CALC_FIRE_ALARM, 
    CALC_WATER_SUPPLY, CALC_ENERGY_CLASS, CALC_WATER_DRAINAGE,
    CALC_FACADE, CALC_FOUNDATION, CALC_PAINTING, CALC_HOLIDAYS,
    CALC_GREEN_SPACES, CALC_HEATING, CALC_MOLD, CALC_WATER_PIPES,
    CALC_ELECTRICITY, CALC_GAS,
    SHOW_RESULT
) = range(22)

# Конфигурация
TOKEN = os.getenv("TOKEN")

# Данные для расчета из Excel
CALC_DATA = {
    # 1 знак - Период строительства
    "period": {
        "A": {"name": "Новостройки (дома, введенные в эксплуатацию после 2015 года)", "value": 1},
        "B": {"name": "Современные (дома, построенные в период с 2000 по 2014 год)", "value": 2},
        "C": {"name": "Типовые (дома массовой застройки, построенные в период с 1970 по 1999 год)", "value": 3},
        "D": {"name": "Старые (дома, построенные в период с 1946 по 1969 год)", "value": 4},
        "E": {"name": "Дореволюционные и ранние советские (дома, построенные до 1945 года)", "value": 5}
    },
    
    # 2 знак - Материал стен
    "wall_material": {
        "A": {"name": "Кирпичные (дома с кирпичными стенами)", "value": 1},
        "B": {"name": "Панельные (дома с панельными стенами)", "value": 2},
        "C": {"name": "Монолитные (дома с монолитными стенами)", "value": 3},
        "D": {"name": "Деревянные (дома с деревянными стенами)", "value": 4},
        "E": {"name": "Смешанные (дома со стенами из разных материалов)", "value": 5}
    },
    
    # 3 знак - Этажность
    "floors": {
        "1": {"name": "Малоэтажные (до 3 этажей)", "value": 4},
        "2": {"name": "Среднеэтажные (от 4 до 9 этажей)", "value": 6},
        "3": {"name": "Многоэтажные (от 10 до 19 этажей)", "value": 8},
        "4": {"name": "Высотные (от 20 этажей и выше)", "value": 10}
    },
    
    # Лифты
    "elevator": {
        "1": {"name": "Отсутствие лифта", "value": 0},
        "2": {"name": "Наличие 1 лифта", "value": 6},
        "3": {"name": "Наличие 2 лифтов", "value": 8},
        "4": {"name": "Наличие 3 и более лифтов", "value": 10}
    },
    
    # Мусоропровод
    "garbage_chute": {
        "1": {"name": "Нет мусоропровода", "value": 0},
        "2": {"name": "Есть мусоропровод", "value": 5}
    },
    
    # Система дымоудаления
    "smoke_removal": {
        "1": {"name": "Статическая (клапаны и заглушки в основной вентиляции)", "value": 2},
        "2": {"name": "Динамическая (активная очистка воздуха)", "value": 4},
        "3": {"name": "Естественная (конвекция, разница давления)", "value": 2},
        "4": {"name": "Принудительная (вентиляторы на крыше/стенах)", "value": 4}
    },
    
    # Пожарная сигнализация
    "fire_alarm": {
        "1": {"name": "Аналоговая", "value": 2},
        "2": {"name": "Пороговая", "value": 4},
        "3": {"name": "Комбинированная", "value": 6},
        "connection_type": {
            "1": {"name": "Радиоканальные", "value": 2},
            "2": {"name": "Проводная", "value": 4},
            "3": {"name": "Комбинированные и оптоволоконные", "value": 6}
        }
    },
    
    # Система водоснабжения
    "water_supply": {
        "1": {"name": "Централизованная система (несколько зданий к одному источнику)", "value": 2},
        "2": {"name": "Нецентрализованная система (один источник на здание)", "value": 6},
        "3": {"name": "Отсутствие системы водоснабжения", "value": 0}
    },
    
    # Класс энергоэффективности
    "energy_class": {
        "1": {"name": "A++ (экономия более 60%)", "value": 2},
        "2": {"name": "A+ (экономия 50-60%)", "value": 4},
        "3": {"name": "A (экономия 40-50%)", "value": 6},
        "4": {"name": "B (экономия 30-40%)", "value": 8},
        "5": {"name": "C (экономия 15-30%)", "value": 10},
        "6": {"name": "D (экономия до 15%)", "value": 12},
        "7": {"name": "E (потеря до 25%)", "value": 14},
        "8": {"name": "F (потеря 25-50%)", "value": 16},
        "9": {"name": "G (потеря более 50%)", "value": 18}
    },
    
    # Система водоотведения
    "water_drainage": {
        "1": {"name": "Хозяйственно-бытовая канализация", "value": 6},
        "2": {"name": "Ливневая канализация", "value": 4},
        "3": {"name": "Производственная канализация", "value": 2},
        "drainage_type": {
            "1": {"name": "Внутренняя канализация", "value": 6},
            "2": {"name": "Общесплавная", "value": 2},
            "3": {"name": "Раздельная", "value": 4},
            "4": {"name": "Полураздельная", "value": 6}
        }
    },
    
    # 4 знак - Состояние фасада
    "facade": {
        "1": {"name": "Отличное состояние (ремонт не требуется)", "value": 2},
        "2": {"name": "Близкое к отличному (требуется единовременный ремонт)", "value": 4},
        "3": {"name": "Среднее состояние (требуется регулярный ремонт)", "value": 6},
        "4": {"name": "Плохое состояние (большие затраты на ремонт)", "value": 8}
    },
    
    # Состояние фундамента
    "foundation": {
        "1": {"name": "Отсутствие трещин (ремонт не требуется)", "value": 0},
        "2": {"name": "Наличие трещин без угрозы целостности", "value": 4},
        "3": {"name": "Критичная ситуация (капитальный ремонт или снос)", "value": 8}
    },
    
    # 5 знак - Покраска территории
    "painting": {
        "1": {"name": "Не требуется", "value": 0},
        "2": {"name": "Требуется 1 раз в год", "value": 2},
        "3": {"name": "Требуется 2 раза в год", "value": 4},
        "4": {"name": "Требуется 4 раза в год", "value": 6}
    },
    
    # Подготовка к праздникам
    "holidays": {
        "1": {"name": "Не требуется", "value": 0},
        "2": {"name": "Только Новый год и 9 мая", "value": 2},
        "3": {"name": "Все государственные праздники", "value": 4},
        "4": {"name": "Расширенный список праздников", "value": 6}
    },
    
    # Уход за зелеными насаждениями
    "green_spaces": {
        "1": {"name": "Не требуется", "value": 0},
        "2": {"name": "Посадка/подрезка 1 раз в год", "value": 1},
        "3": {"name": "Регулярный уход (полив, подрезка)", "value": 2}
    },
    
    # Состояние отопительной системы
    "heating": {
        "1": {"name": "Не требует ремонта", "value": 1},
        "2": {"name": "Некритичная коррозия", "value": 2},
        "3": {"name": "Критичное состояние (течи, возраст более 20 лет)", "value": 4}
    },
    
    # Поражение грибком/плесенью
    "mold": {
        "1": {"name": "Отсутствует", "value": 0},
        "2": {"name": "Некритичное (в отдельных участках)", "value": 1},
        "3": {"name": "Усиливается после зимы", "value": 2},
        "4": {"name": "Круглогодичное (затрагивает несущие элементы)", "value": 4}
    },
    
    # Состояние водопроводных труб
    "water_pipes": {
        "1": {"name": "Не требует ремонта", "value": 0},
        "2": {"name": "Некритичные повреждения", "value": 1},
        "3": {"name": "Течи после отопительного сезона", "value": 2},
        "4": {"name": "Критичное состояние (требуется замена системы)", "value": 4}
    },
    
    # Состояние электропроводки
    "electricity": {
        "1": {"name": "Не требует ремонта", "value": 0},
        "2": {"name": "Некритичные повреждения", "value": 2},
        "3": {"name": "Нерегулярные отключения", "value": 4},
        "4": {"name": "Критичное состояние (оголенные провода)", "value": 6}
    },
    
    # Состояние газовой системы
    "gas": {
        "1": {"name": "Отсутствие утечек", "value": 1},
        "2": {"name": "Наличие утечек", "value": 4},
        "3": {"name": "Изолирована после ЧП", "value": 6}
    }
}

# Классы зданий
BUILDING_CLASSES = {
    "1": {"name": "Самые низкие затраты", "range": ("АА", "ВА")},
    "2": {"name": "Средние затраты", "range": ("АБ", "ВД")},
    "3": {"name": "Самые высокие затраты", "range": ("ГА", "ДД")}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("Рассчитать стоимость услуг", callback_data="calculate_cost")],
        [InlineKeyboardButton("Поддержка", callback_data="support")],
        [InlineKeyboardButton("Очистить чат", callback_data="clear_chat")],
        [InlineKeyboardButton("GitHub", url="https://github.com")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=markup)
    else:
        await update.callback_query.edit_message_text("Добро пожаловать! Выберите действие:", reply_markup=markup)
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🆘 Список команд:\n"
        "/start – Главное меню\n"
        "/help – Помощь и команды\n"
        "/clear – Очистить чат (символически)\n\n"
        "Вы также можете пользоваться кнопками внутри бота."
    )
    await update.message.reply_text(text)

async def support_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "📞 +7 (123) 456-78-90\n📧 support@example.com\n🕒 9:00-18:00 (Пн-Пт)",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_to_start")]])
    )

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "История очищена (символически).",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back_to_start")]])
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Очистка истории недоступна через API Telegram. Используйте кнопку в меню.")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "calculate_cost":
        return await start_calculation(update, context)
    elif data == "support":
        return await support_info(update, context)
    elif data == "clear_chat":
        return await clear_chat(update, context)
    elif data == "back_to_start":
        return await start(update, context)
    
    # Обработка кнопок для расчета стоимости
    if data.startswith("calc_"):
        parts = data.split("_")
        if len(parts) >= 3:
            category = parts[1]
            choice = parts[2]
            
            # Исправляем ключи для категорий с подчеркиванием
            if category == "garbage":
                category = "garbage_chute"
            elif category == "wall":
                category = "wall_material"
            elif category == "smoke":
                category = "smoke_removal"
            # Добавьте другие аналогичные преобразования при необходимости
            
            # Сохраняем выбор пользователя
            context.user_data[category] = choice
            
            # Определяем следующий шаг
            next_state = determine_next_state(category)
            
            if next_state == SHOW_RESULT:
                return await show_result(update, context)
            else:
                return await ask_question(update, context, next_state)
    
    return ConversationHandler.END

def determine_next_state(current_category):
    """Определяет следующее состояние на основе текущей категории"""
    state_mapping = {
        "period": CALC_PERIOD,
        "wall_material": CALC_WALL_MATERIAL,
        "floors": CALC_FLOORS,
        "elevator": CALC_ELEVATOR,
        "garbage_chute": CALC_GARBAGE_CHUTE,
        "smoke_removal": CALC_SMOKE_REMOVAL,
        "fire_alarm": CALC_FIRE_ALARM,
        "water_supply": CALC_WATER_SUPPLY,
        "energy_class": CALC_ENERGY_CLASS,
        "water_drainage":  CALC_WATER_DRAINAGE,
        "facade": CALC_FACADE,
        "foundation": CALC_FOUNDATION,
        "painting": CALC_PAINTING,
        "holidays": CALC_HOLIDAYS,
        "green_spaces": CALC_GREEN_SPACES,
        "heating": CALC_HEATING,
        "mold": CALC_MOLD,
        "water_pipes": CALC_WATER_PIPES,
        "electricity": CALC_ELECTRICITY,
        "gas": CALC_GAS,
        "result": SHOW_RESULT
    }
    return state_mapping.get(current_category, SHOW_RESULT)

async def start_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.callback_query.edit_message_text(
        "🔢 Начинаем расчет стоимости услуг. Будет задано несколько вопросов о вашем здании.\n\n"
        "1️⃣ Первый знак: период строительства",
        reply_markup=get_keyboard("period")
    )
    return CALC_PERIOD

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    questions = {
        CALC_PERIOD: ("1️⃣ Первый знак: период строительства", "period"),
        CALC_WALL_MATERIAL: ("2️⃣ Второй знак: материал стен", "wall_material"),
        CALC_FLOORS: ("3️⃣ Третий знак: этажность здания", "floors"),
        CALC_ELEVATOR: ("Наличие лифтов", "elevator"),
        CALC_GARBAGE_CHUTE: ("Наличие мусоропровода", "garbage_chute"),
        CALC_SMOKE_REMOVAL: ("Система дымоудаления", "smoke_removal"),
        CALC_FIRE_ALARM: ("Тип пожарной сигнализации", "fire_alarm"),
        CALC_WATER_SUPPLY: ("Система водоснабжения", "water_supply"),
        CALC_ENERGY_CLASS: ("Класс энергоэффективности", "energy_class"),
        CALC_WATER_DRAINAGE: ("Система водоотведения", "water_drainage"),
        CALC_FACADE: ("4️⃣ Четвертый знак: состояние фасада", "facade"),
        CALC_FOUNDATION: ("Состояние фундамента", "foundation"),
        CALC_PAINTING: ("5️⃣ Пятый знак: покраска территории", "painting"),
        CALC_HOLIDAYS: ("Подготовка к праздникам", "holidays"),
        CALC_GREEN_SPACES: ("Уход за зелеными насаждениями", "green_spaces"),
        CALC_HEATING: ("Состояние отопительной системы", "heating"),
        CALC_MOLD: ("Поражение грибком/плесенью", "mold"),
        CALC_WATER_PIPES: ("Состояние водопроводных труб", "water_pipes"),
        CALC_ELECTRICITY: ("Состояние электропроводки", "electricity"),
        CALC_GAS: ("Состояние газовой системы", "gas")
    }
    
    question, category = questions.get(state, ("", ""))
    if not question:
        return await show_result(update, context)
    
    await update.callback_query.edit_message_text(
        question,
        reply_markup=get_keyboard(category)
    )
    return state


def get_keyboard(category):
    """Создает клавиатуру с вариантами ответа для категории"""
    buttons = []
    data = CALC_DATA.get(category, {})
    
    # Для всех категорий
    for key, value in data.items():
        if isinstance(value, dict) and not key.endswith("_type") and not key.endswith("_connection"):
            # Генерируем callback_data с правильными именами категорий
            callback_category = category
            if category == "garbage_chute":
                callback_category = "garbage"  # Используем короткое имя в callback
            elif category == "wall_material":
                callback_category = "wall"
            elif category == "smoke_removal":
                callback_category = "smoke"
            elif category == 
            # Продолжи далее
            # Добавьте другие аналогичные преобразования при необходимости
            
            buttons.append([InlineKeyboardButton(
                f"{key} - {value['name']}",
                callback_data=f"calc_{callback_category}_{key}"
            )])
    
    # Добавляем кнопку "Назад" только если это не первый вопрос
    if category != "period":
        buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_calc_start")])
    
    return InlineKeyboardMarkup(buttons)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает итоговый результат расчета"""
    # Собираем все выбранные значения
    user_data = context.user_data
    
    # Рассчитываем общую сумму баллов
    total_score = 0
    details = []
    
    # 1 знак - период строительства
    period = user_data.get("period", "А")
    period_data = CALC_DATA["period"][period]
    total_score += period_data["value"]
    details.append(f"1️⃣ Период строительства: {period_data['name']} ({period_data['value']} баллов)")
    
    # 2 знак - материал стен
    material = user_data.get("wall_material", "A")  # Используем "wall_material" вместо "material"
    material_data = CALC_DATA["wall_material"][material]
    total_score += material_data["value"]
    details.append(f"2️⃣ Материал стен: {material_data['name']} ({material_data['value']} баллов)")
    
    # 3 знак - этажность
    floors = user_data.get("floors", "1")
    floors_data = CALC_DATA["floors"][floors]
    total_score += floors_data["value"]
    details.append(f"3️⃣ Этажность: {floors_data['name']} ({floors_data['value']} баллов)")
    
    # Лифты
    elevator = user_data.get("elevator", "1")
    elevator_data = CALC_DATA["elevator"][elevator]
    total_score += elevator_data["value"]
    details.append(f"Лифты: {elevator_data['name']} ({elevator_data['value']} баллов)")
    
    # Мусоропровод
    garbage = user_data.get("garbage", "1")
    garbage_data = CALC_DATA["garbage_chute"][garbage]
    total_score += garbage_data["value"]
    details.append(f"Мусоропровод: {garbage_data['name']} ({garbage_data['value']} баллов)")
    
    # Система дымоудаления
    smoke = user_data.get("smoke_removal", "1")
    smoke_data = CALC_DATA["smoke_removal"][smoke]
    total_score += smoke_data["value"]
    details.append(f"Система дымоудаления: {smoke_data['name']} ({smoke_data['value']} баллов)")
    
    # Пожарная сигнализация
    fire = user_data.get("fire", "1")
    fire_data = CALC_DATA["fire_alarm"][fire]
    total_score += fire_data["value"]
    details.append(f"Пожарная сигнализация (тип): {fire_data['name']} ({fire_data['value']} баллов)")
    
    # Водоснабжение
    water = user_data.get("water", "1")
    water_data = CALC_DATA["water_supply"][water]
    total_score += water_data["value"]
    details.append(f"Водоснабжение: {water_data['name']} ({water_data['value']} баллов)")
    
    # Класс энергоэффективности
    energy = user_data.get("energy", "1")
    energy_data = CALC_DATA["energy_class"][energy]
    total_score += energy_data["value"]
    details.append(f"Класс энергоэффективности: {energy_data['name']} ({energy_data['value']} баллов)")
    
    # Водоотведение
    drainage = user_data.get("drainage", "1")
    drainage_data = CALC_DATA["water_drainage"][drainage]
    total_score += drainage_data["value"]
    details.append(f"Водоотведение: {drainage_data['name']} ({drainage_data['value']} баллов)")
    
    # 4 знак - состояние фасада
    facade = user_data.get("facade", "1")
    facade_data = CALC_DATA["facade"][facade]
    total_score += facade_data["value"]
    details.append(f"4️⃣ Состояние фасада: {facade_data['name']} ({facade_data['value']} баллов)")
    
    # Фундамент
    foundation = user_data.get("foundation", "1")
    foundation_data = CALC_DATA["foundation"][foundation]
    total_score += foundation_data["value"]
    details.append(f"Фундамент: {foundation_data['name']} ({foundation_data['value']} баллов)")
    
    # 5 знак - покраска территории
    painting = user_data.get("painting", "1")
    painting_data = CALC_DATA["painting"][painting]
    total_score += painting_data["value"]
    details.append(f"5️⃣ Покраска территории: {painting_data['name']} ({painting_data['value']} баллов)")
    
    # Подготовка к праздникам
    holidays = user_data.get("holidays", "1")
    holidays_data = CALC_DATA["holidays"][holidays]
    total_score += holidays_data["value"]
    details.append(f"Подготовка к праздникам: {holidays_data['name']} ({holidays_data['value']} баллов)")
    
    # Уход за зелеными насаждениями
    green = user_data.get("green", "1")
    green_data = CALC_DATA["green_spaces"][green]
    total_score += green_data["value"]
    details.append(f"Уход за зелеными насаждениями: {green_data['name']} ({green_data['value']} баллов)")
    
    # Отопительная система
    heating = user_data.get("heating", "1")
    heating_data = CALC_DATA["heating"][heating]
    total_score += heating_data["value"]
    details.append(f"Отопительная система: {heating_data['name']} ({heating_data['value']} баллов)")
    
    # Поражение грибком
    mold = user_data.get("mold", "1")
    mold_data = CALC_DATA["mold"][mold]
    total_score += mold_data["value"]
    details.append(f"Поражение грибком: {mold_data['name']} ({mold_data['value']} баллов)")
    
    # Водопроводные трубы
    pipes = user_data.get("pipes", "1")
    pipes_data = CALC_DATA["water_pipes"][pipes]
    total_score += pipes_data["value"]
    details.append(f"Водопроводные трубы: {pipes_data['name']} ({pipes_data['value']} баллов)")
    
    # Электропроводка
    electricity = user_data.get("electricity", "1")
    electricity_data = CALC_DATA["electricity"][electricity]
    total_score += electricity_data["value"]
    details.append(f"Электропроводка: {electricity_data['name']} ({electricity_data['value']} баллов)")
    
    # Газовая система
    gas = user_data.get("gas", "1")
    gas_data = CALC_DATA["gas"][gas]
    total_score += gas_data["value"]
    details.append(f"Газовая система: {gas_data['name']} ({gas_data['value']} баллов)")
    
    # Определяем класс здания
    building_class = determine_building_class(period, material)
    class_data = BUILDING_CLASSES[building_class]
    
    # Формируем итоговое сообщение
    result_message = (
        f"🏢 <b>Результаты расчета</b> 🏢\n\n"
        f"🔢 <b>Итоговый балл:</b> {total_score}\n"
        f"🏷️ <b>Класс здания:</b> {class_data['name']} ({class_data['range'][0]}-{class_data['range'][1]})\n"
        f"🔤 <b>Код здания:</b> {period}{material}{floors}{facade}{painting}{holidays[0]}\n\n"
        f"<b>Детали расчета:</b>\n" + "\n".join(details)
    )
    
    keyboard = [
        [InlineKeyboardButton("Начать новый расчет", callback_data="calculate_cost")],
        [InlineKeyboardButton("В главное меню", callback_data="back_to_start")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        result_message,
        reply_markup=markup,
        parse_mode="HTML"
    )
    return SHOW_RESULT

def determine_building_class(period, material):
    """Определяет класс здания на основе периода и материала"""
    # Простая логика определения класса (можно усложнить)
    if period in ["А", "Б"] and material in ["А", "В"]:
        return "1"  # Самые низкие затраты
    elif period in ["В", "Г"] and material in ["Б", "Д"]:
        return "3"  # Самые высокие затраты
    else:
        return "2"  # Средние затраты

async def back_to_calc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к началу расчета"""
    return await start_calculation(update, context)

async def set_bot_commands(app: Application):
    commands = [
        BotCommand("start", "Главное меню"),
        BotCommand("help", "Помощь и команды"),
        BotCommand("clear", "Очистка чата (символическая)")
    ]
    await app.bot.set_my_commands(commands)

def main():
    app = Application.builder().token(TOKEN).build()

    # Обработчики для расчета стоимости
    calc_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_calculation, pattern="^calculate_cost$")],
        states={
            CALC_PERIOD: [CallbackQueryHandler(button_click, pattern="^calc_period_")],
            CALC_WALL_MATERIAL: [CallbackQueryHandler(button_click, pattern="^calc_material_")],
            CALC_FLOORS: [CallbackQueryHandler(button_click, pattern="^calc_floors_")],
            CALC_ELEVATOR: [CallbackQueryHandler(button_click, pattern="^calc_elevator_")],
            CALC_GARBAGE_CHUTE: [CallbackQueryHandler(button_click, pattern="^calc_garbage_")],
            CALC_SMOKE_REMOVAL: [CallbackQueryHandler(button_click, pattern="^calc_smoke_")],
            CALC_FIRE_ALARM: [CallbackQueryHandler(button_click, pattern="^calc_fire_")],
            CALC_WATER_SUPPLY: [CallbackQueryHandler(button_click, pattern="^calc_water_")],
            CALC_ENERGY_CLASS: [CallbackQueryHandler(button_click, pattern="^calc_energy_")],
            CALC_WATER_DRAINAGE: [CallbackQueryHandler(button_click, pattern="^calc_drainage_")],
            CALC_FACADE: [CallbackQueryHandler(button_click, pattern="^calc_facade_")],
            CALC_FOUNDATION: [CallbackQueryHandler(button_click, pattern="^calc_foundation_")],
            CALC_PAINTING: [CallbackQueryHandler(button_click, pattern="^calc_painting_")],
            CALC_HOLIDAYS: [CallbackQueryHandler(button_click, pattern="^calc_holidays_")],
            CALC_GREEN_SPACES: [CallbackQueryHandler(button_click, pattern="^calc_green_")],
            CALC_HEATING: [CallbackQueryHandler(button_click, pattern="^calc_heating_")],
            CALC_MOLD: [CallbackQueryHandler(button_click, pattern="^calc_mold_")],
            CALC_WATER_PIPES: [CallbackQueryHandler(button_click, pattern="^calc_pipes_")],
            CALC_ELECTRICITY: [CallbackQueryHandler(button_click, pattern="^calc_electricity_")],
            CALC_GAS: [CallbackQueryHandler(button_click, pattern="^calc_gas_")],
            SHOW_RESULT: [
                CallbackQueryHandler(start_calculation, pattern="^calculate_cost$"),
                CallbackQueryHandler(start, pattern="^back_to_start$")
            ]
        },
        fallbacks=[
            CallbackQueryHandler(back_to_calc_start, pattern="^back_to_calc_start$"),
            CommandHandler("start", start)
        ]
    )

    app.add_handler(calc_conv_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CallbackQueryHandler(button_click))

    app.post_init = set_bot_commands
    app.run_polling()

if __name__ == "__main__":
    main()