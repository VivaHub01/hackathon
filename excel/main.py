import pandas as pd

# Базы данных характеристик
construction_periods = {
    "A": "Новостройки (после 2015)",
    "B": "Современные (2000-2014)", 
    "C": "Типовые (1970-1999)",
    "D": "Старые (1946-1969)",
    "E": "Дореволюционные (до 1945)"
}

wall_materials = {
    "A": "Кирпичные",
    "B": "Панельные",
    "C": "Монолитные", 
    "D": "Деревянные",
    "E": "Смешанные"
}

# Параметры для третьего знака
third_sign_params = {
    "Этажность": {
        "1": {"name": "Малоэтажные", "range": "До 3", "value": 4},
        "2": {"name": "Среднеэтажные", "range": "От 4 до 9", "value": 6},
        "3": {"name": "Многоэтажные", "range": "От 10 до 19", "value": 8},
        "4": {"name": "Высотные", "range": "От 20 и выше", "value": 10}
    },
    "Лифты": {
        "1": {"name": "Отсутствие лифта", "value": 0},
        "2": {"name": "1 лифт", "value": 6},
        "3": {"name": "2 лифта", "value": 8},
        "4": {"name": "3+ лифтов", "value": 10}
    },
    "Мусоропровод": {
        "1": {"name": "Нет мусоропровода", "value": 0},
        "2": {"name": "Есть мусоропровод", "value": 5}
    },
    "Система дымоудаления": {
        "1": {"name": "Статическая", "desc": "Состоят из клапанов и заглушек, встроенных в основную вентиляцию", "value": 2},
        "2": {"name": "Динамическая", "desc": "Не только уменьшают задымление, но и активно очищают воздух от продуктов горения", "value": 4}
    },
    "Вентиляция": {
        "1": {"name": "Естественная", "desc": "Удаляют продукты горения из помещения с помощью естественных процессов", "value": 2},
        "2": {"name": "Принудительная", "desc": "Осуществляют очистку воздуха от продуктов горения активным воздухообменом", "value": 4}
    },
    "Тип АПС по информации": {
        "1": {"name": "Аналоговая", "desc": "По типу передаваемой информации", "value": 2},
        "2": {"name": "Пороговая", "desc": "По типу передаваемой информации", "value": 4},
        "3": {"name": "Комбинированная", "desc": "По типу передаваемой информации", "value": 6}
    },
    "Тип АПС по связи": {
        "1": {"name": "Радиоканальные", "desc": "По типу физической реализации связи", "value": 2},
        "2": {"name": "Проводная", "desc": "По типу физической реализации связи", "value": 4},
        "3": {"name": "Комбинированные и оптоволоконные", "desc": "По типу физической реализации связи", "value": 6}
    },
    "Система водоснабжения": {
        "1": {"name": "Централизированная система", "desc": "Подключение нескольких зданий к одному 'котлу'", "value": 2},
        "2": {"name": "Нецентрализованная система", "desc": "Один 'котел' на одно здание", "value": 6},
        "3": {"name": "Отсутствие системы водоснабжения", "desc": "Органы местного самоуправления обязаны обеспечить нецентрализованное холодное водоснабжение", "value": 0}
    },
    "Класс энергоэффективности": {
        "1": {"name": "A++", "desc": "Экономия более 60%", "value": 2},
        "2": {"name": "A+", "desc": "Экономия от 50 до 60%", "value": 4},
        "3": {"name": "A", "desc": "Экономия от 40 до 50%", "value": 6},
        "4": {"name": "B", "desc": "Экономия от 30 до 40%", "value": 8},
        "5": {"name": "C", "desc": "Экономия от 15 до 30%", "value": 10},
        "6": {"name": "D", "desc": "Экономия до 15%", "value": 12},
        "7": {"name": "E", "desc": "Потеря до 25%", "value": 14},
        "8": {"name": "F", "desc": "Потеря от 25 до 50%", "value": 16},
        "9": {"name": "G", "desc": "Потеря более 50%", "value": 18}
    },
    "Тип канализации": {
        "1": {"name": "Хозяйственно-бытовая или хозфекальная", "desc": "Загрязнения преимущественно связаны с обычной жизнедеятельностью человека", "value": 6},
        "2": {"name": "Ливневая", "desc": "Служит для отведения воды с поверхности грунта", "value": 4},
        "3": {"name": "Производственная", "desc": "Внедряется на промышленных предприятиях", "value": 2}
    },
    "Конструкция канализации": {
        "1": {"name": "Внутренняя", "desc": "Комплекс канализационных устройств внутри здания", "value": 6},
        "2": {"name": "Общесплавная", "desc": "Все сточные воды транспортируются общим потоком", "value": 2},
        "3": {"name": "Раздельная", "desc": "Хозяйственно-бытовые, промышленные и ливневые стоки имеют раздельные отводы", "value": 4},
        "4": {"name": "Полураздельная", "desc": "Вода из разных отводов помещается в общую очистную систему", "value": 6}
    }
}

# Параметры для четвертого знака
fourth_sign_params = {
    "Состояние фасада здания": {
        "1": {"name": "Отличное состояние", "desc": "Ремонт здания не требуется", "value": 1},
        "2": {"name": "Близкое к отличному", "desc": "Требуется единовременный ремонт", "value": 4},
        "3": {"name": "Среднее состояние", "desc": "Требуется регулярный периодичный ремонт", "value": 6},
        "4": {"name": "Плохое состояние", "desc": "Регулярный ремонт наносит большой ущерб и финансовых затрат", "value": 8}
    },
    "Состояние фундамента здания": {
        "1": {"name": "Отсутствие трещин", "desc": "Ремонт не требуется", "value": 0},
        "2": {"name": "Неопасные трещины", "desc": "Требуется ремонт", "value": 4},
        "3": {"name": "Критичная ситуация", "desc": "Капитальный ремонт или снос", "value": 8}
    },
    "Состояние отопительных систем": {
        "1": {"name": "Не требует ремонта", "desc": "Требуется только периодический осмотр", "value": 1},
        "2": {"name": "Некритичная коррозия", "desc": "Наличие видимой коррозии, не влияющей на эффективность", "value": 2},
        "3": {"name": "Критичное состояние", "desc": "Снижение эффективности работы отопительных систем", "value": 4}
    },
    "Степень поражения грибком плесени": {
        "1": {"name": "Отсутствует", "desc": "Требуется только периодический осмотр", "value": 0},
        "2": {"name": "Некритичное", "desc": "Поражение в отдельных участках", "value": 1},
        "3": {"name": "Сезонное", "desc": "Усиливается после зимнего сезона", "value": 2},
        "4": {"name": "Критичное", "desc": "Круглогодичное поражение несущих элементов", "value": 4}
    },
    "Состояние водопроводных труб": {
        "1": {"name": "Не требует ремонта", "desc": "Требуется только периодический осмотр", "value": 0},
        "2": {"name": "Некритичные повреждения", "desc": "Поражение в отдельных участках", "value": 1},
        "3": {"name": "Сезонные проблемы", "desc": "Усиливается после отопительного сезона", "value": 2},
        "4": {"name": "Критичное", "desc": "Круглогодичное поражение несущих элементов", "value": 4}
    },
    "Состояние электрической проводки": {
        "1": {"name": "Не требует ремонта", "desc": "Требуется только периодический осмотр", "value": 0},
        "2": {"name": "Некритичные повреждения", "desc": "Поражение в отдельных участках", "value": 2},
        "3": {"name": "Периодические сбои", "desc": "Наличие нерегулярных отключений", "value": 4},
        "4": {"name": "Критичное состояние", "desc": "Регулярные сбои, оголенные контакты", "value": 6}
    },
    "Состояние газовой системы": {
        "1": {"name": "Нормальное", "desc": "Отсутствие утечек газа", "value": 1},
        "2": {"name": "Утечка газа", "desc": "Требуется перекрытие системы", "value": 4},
        "3": {"name": "Аварийное", "desc": "Изоляция системы после ЧС", "value": 6}
    }
}

# Параметры для пятого знака
fifth_sign_params = {
    "Покраска придомовой территории": {
        "1": {"name": "Не требуется", "desc": "Отсутствие элементов, требующих перекраски", "value": 0},
        "2": {"name": "1 раз в год", "desc": "Покраска элементов раз в год", "value": 2},
        "3": {"name": "2 раза в год", "desc": "Покраска элементов два раза в год", "value": 4},
        "4": {"name": "4 раза в год", "desc": "Покраска элементов четыре раза в год", "value": 6}
    },
    "Уход за придомовой зеленью": {
        "1": {"name": "Не требуется", "desc": "Минимальный уход", "value": 0},
        "2": {"name": "1 раз в год", "desc": "Посадка и подрезка раз в год", "value": 1},
        "3": {"name": "Регулярный уход", "desc": "Постоянный уход за растениями", "value": 2}
    }
}

# Параметры для шестого знака
sixth_sign_params = {
    "Подготовка к праздникам": {
        "1": {"name": "Не требуется", "desc": "Отсутствие праздничного оформления", "value": 0},
        "2": {"name": "НГ и 9 мая", "desc": "Украшение к Новому году и Дню Победы", "value": 2},
        "3": {"name": "Гос праздники", "desc": "Украшение к государственным праздникам", "value": 4},
        "4": {"name": "Расширенный список", "desc": "Украшение к каждому празднику", "value": 6}
    }
}

def get_choice(options_dict, prompt, numeric=False):
    print(f"\n{prompt}:")
    
    if numeric and isinstance(next(iter(options_dict.values())), dict):
        for key, data in options_dict.items():
            if "desc" in data:
                print(f"{key}: {data['name']} - {data['desc']} (балл: {data['value']})")
            elif "range" in data:
                print(f"{key}: {data['name']} ({data['range']}) (балл: {data['value']})")
            else:
                print(f"{key}: {data['name']} (балл: {data['value']})")
    else:
        for key, desc in options_dict.items():
            print(f"{key}: {desc}")
    
    while True:
        valid_keys = list(options_dict.keys())
        input_prompt = f"Введите {'цифру' if numeric else 'букву'} ({'/'.join(valid_keys)}): "
        choice = input(input_prompt).strip().upper()
        
        if choice in valid_keys:
            return choice
        print(f"Ошибка! Допустимые значения: {', '.join(valid_keys)}")

# Получаем данные от пользователя
print("=== Введите характеристики здания ===")
period = get_choice(construction_periods, "1. Период строительства")
material = get_choice(wall_materials, "2. Материал стен")

# Получаем данные для третьего знака
print("\n=== 3. Технические характеристики ===")
height = get_choice(third_sign_params["Этажность"], "Этажность", numeric=True)
elevator = get_choice(third_sign_params["Лифты"], "Наличие лифтов", numeric=True)
garbage = get_choice(third_sign_params["Мусоропровод"], "Наличие мусоропровода", numeric=True)
smoke_removal = get_choice(third_sign_params["Система дымоудаления"], "Вид системы дымоудаления", numeric=True)
ventilation = get_choice(third_sign_params["Вентиляция"], "Тип вентиляции", numeric=True)
aps_info = get_choice(third_sign_params["Тип АПС по информации"], "Тип АПС по информации", numeric=True)
aps_connection = get_choice(third_sign_params["Тип АПС по связи"], "Тип АПС по связи", numeric=True)
water_supply = get_choice(third_sign_params["Система водоснабжения"], "Система водоснабжения", numeric=True)
energy_class = get_choice(third_sign_params["Класс энергоэффективности"], "Класс энергоэффективности", numeric=True)
drainage_type = get_choice(third_sign_params["Тип канализации"], "Тип канализации", numeric=True)
drainage_design = get_choice(third_sign_params["Конструкция канализации"], "Конструкция канализации", numeric=True)

# Получаем данные для четвертого знака
print("\n=== 4. Состояние здания ===")
facade_condition = get_choice(fourth_sign_params["Состояние фасада здания"], "Состояние фасада здания", numeric=True)
foundation_condition = get_choice(fourth_sign_params["Состояние фундамента здания"], "Состояние фундамента здания", numeric=True)
heating_condition = get_choice(fourth_sign_params["Состояние отопительных систем"], "Состояние отопительных систем", numeric=True)
mold_condition = get_choice(fourth_sign_params["Степень поражения грибком плесени"], "Степень поражения грибком плесени", numeric=True)
plumbing_condition = get_choice(fourth_sign_params["Состояние водопроводных труб"], "Состояние водопроводных труб", numeric=True)
electrical_condition = get_choice(fourth_sign_params["Состояние электрической проводки"], "Состояние электрической проводки", numeric=True)
gas_condition = get_choice(fourth_sign_params["Состояние газовой системы"], "Состояние газовой системы", numeric=True)

# Получаем данные для пятого знака
print("\n=== 5. Придомовая территория ===")
painting_frequency = get_choice(fifth_sign_params["Покраска придомовой территории"], "Покраска придомовой территории", numeric=True)
greenery_care = get_choice(fifth_sign_params["Уход за придомовой зеленью"], "Уход за придомовой зеленью", numeric=True)

# Получаем данные для шестого знака
print("\n=== 6. Праздничное оформление ===")
holiday_preparation = get_choice(sixth_sign_params["Подготовка к праздникам"], "Подготовка к праздникам", numeric=True)

# Рассчитываем суммы баллов для объединенных параметров
smoke_vent_score = (third_sign_params['Система дымоудаления'][smoke_removal]['value'] + 
                   third_sign_params['Вентиляция'][ventilation]['value'])

aps_score = (third_sign_params['Тип АПС по информации'][aps_info]['value'] + 
            third_sign_params['Тип АПС по связи'][aps_connection]['value'])

drainage_score = (third_sign_params['Тип канализации'][drainage_type]['value'] + 
                third_sign_params['Конструкция канализации'][drainage_design]['value'])

# Формируем данные для таблицы
data = [
    {"Знак": 1, "Параметр": "Период строительства", "Код": period, "Описание": construction_periods[period], "Балл": "", "Итог": period},
    {"Знак": 2, "Параметр": "Материал стен", "Код": material, "Описание": wall_materials[material], "Балл": "", "Итог": material},
    
    # Третий знак
    {"Знак": 3, "Параметр": "Этажность", 
     "Код": height, 
     "Описание": f"{third_sign_params['Этажность'][height]['name']} ({third_sign_params['Этажность'][height]['range']})",
     "Балл": third_sign_params['Этажность'][height]['value'],
     "Итог": third_sign_params['Этажность'][height]['value']},
    {"Знак": 3, "Параметр": "Лифты", 
     "Код": elevator, 
     "Описание": third_sign_params['Лифты'][elevator]['name'],
     "Балл": third_sign_params['Лифты'][elevator]['value'],
     "Итог": third_sign_params['Лифты'][elevator]['value']},
    {"Знак": 3, "Параметр": "Мусоропровод", 
     "Код": garbage, 
     "Описание": third_sign_params['Мусоропровод'][garbage]['name'],
     "Балл": third_sign_params['Мусоропровод'][garbage]['value'],
     "Итог": third_sign_params['Мусоропровод'][garbage]['value']},
    {"Знак": 3, "Параметр": "Система дымоудаления и вентиляция", 
     "Код": f"{smoke_removal}/{ventilation}", 
     "Описание": f"{third_sign_params['Система дымоудаления'][smoke_removal]['name']} + {third_sign_params['Вентиляция'][ventilation]['name']}",
     "Балл": f"{third_sign_params['Система дымоудаления'][smoke_removal]['value']}+{third_sign_params['Вентиляция'][ventilation]['value']}",
     "Итог": smoke_vent_score},
    {"Знак": 3, "Параметр": "Автоматическая пожарная сигнализация", 
     "Код": f"{aps_info}/{aps_connection}", 
     "Описание": f"{third_sign_params['Тип АПС по информации'][aps_info]['name']} + {third_sign_params['Тип АПС по связи'][aps_connection]['name']}",
     "Балл": f"{third_sign_params['Тип АПС по информации'][aps_info]['value']}+{third_sign_params['Тип АПС по связи'][aps_connection]['value']}",
     "Итог": aps_score},
    {"Знак": 3, "Параметр": "Система водоснабжения", 
     "Код": water_supply, 
     "Описание": f"{third_sign_params['Система водоснабжения'][water_supply]['name']} - {third_sign_params['Система водоснабжения'][water_supply]['desc']}",
     "Балл": third_sign_params['Система водоснабжения'][water_supply]['value'],
     "Итог": third_sign_params['Система водоснабжения'][water_supply]['value']},
    {"Знак": 3, "Параметр": "Класс энергоэффективности", 
     "Код": energy_class, 
     "Описание": f"{third_sign_params['Класс энергоэффективности'][energy_class]['name']} - {third_sign_params['Класс энергоэффективности'][energy_class]['desc']}",
     "Балл": third_sign_params['Класс энергоэффективности'][energy_class]['value'],
     "Итог": third_sign_params['Класс энергоэффективности'][energy_class]['value']},
    {"Знак": 3, "Параметр": "Система водоотведения", 
     "Код": f"{drainage_type}/{drainage_design}", 
     "Описание": f"{third_sign_params['Тип канализации'][drainage_type]['name']} + {third_sign_params['Конструкция канализации'][drainage_design]['name']}",
     "Балл": f"{third_sign_params['Тип канализации'][drainage_type]['value']}+{third_sign_params['Конструкция канализации'][drainage_design]['value']}",
     "Итог": drainage_score},
    
    # Четвертый знак
    {"Знак": 4, "Параметр": "Состояние фасада здания", 
     "Код": facade_condition, 
     "Описание": f"{fourth_sign_params['Состояние фасада здания'][facade_condition]['name']} - {fourth_sign_params['Состояние фасада здания'][facade_condition]['desc']}",
     "Балл": fourth_sign_params['Состояние фасада здания'][facade_condition]['value'],
     "Итог": fourth_sign_params['Состояние фасада здания'][facade_condition]['value']},
    {"Знак": 4, "Параметр": "Состояние фундамента здания", 
     "Код": foundation_condition, 
     "Описание": f"{fourth_sign_params['Состояние фундамента здания'][foundation_condition]['name']} - {fourth_sign_params['Состояние фундамента здания'][foundation_condition]['desc']}",
     "Балл": fourth_sign_params['Состояние фундамента здания'][foundation_condition]['value'],
     "Итог": fourth_sign_params['Состояние фундамента здания'][foundation_condition]['value']},
    {"Знак": 4, "Параметр": "Состояние отопительных систем", 
     "Код": heating_condition, 
     "Описание": f"{fourth_sign_params['Состояние отопительных систем'][heating_condition]['name']} - {fourth_sign_params['Состояние отопительных систем'][heating_condition]['desc']}",
     "Балл": fourth_sign_params['Состояние отопительных систем'][heating_condition]['value'],
     "Итог": fourth_sign_params['Состояние отопительных систем'][heating_condition]['value']},
    {"Знак": 4, "Параметр": "Степень поражения грибком плесени", 
     "Код": mold_condition, 
     "Описание": f"{fourth_sign_params['Степень поражения грибком плесени'][mold_condition]['name']} - {fourth_sign_params['Степень поражения грибком плесени'][mold_condition]['desc']}",
     "Балл": fourth_sign_params['Степень поражения грибком плесени'][mold_condition]['value'],
     "Итог": fourth_sign_params['Степень поражения грибком плесени'][mold_condition]['value']},
    {"Знак": 4, "Параметр": "Состояние водопроводных труб", 
     "Код": plumbing_condition, 
     "Описание": f"{fourth_sign_params['Состояние водопроводных труб'][plumbing_condition]['name']} - {fourth_sign_params['Состояние водопроводных труб'][plumbing_condition]['desc']}",
     "Балл": fourth_sign_params['Состояние водопроводных труб'][plumbing_condition]['value'],
     "Итог": fourth_sign_params['Состояние водопроводных труб'][plumbing_condition]['value']},
    {"Знак": 4, "Параметр": "Состояние электрической проводки", 
     "Код": electrical_condition, 
     "Описание": f"{fourth_sign_params['Состояние электрической проводки'][electrical_condition]['name']} - {fourth_sign_params['Состояние электрической проводки'][electrical_condition]['desc']}",
     "Балл": fourth_sign_params['Состояние электрической проводки'][electrical_condition]['value'],
     "Итог": fourth_sign_params['Состояние электрической проводки'][electrical_condition]['value']},
    {"Знак": 4, "Параметр": "Состояние газовой системы", 
     "Код": gas_condition, 
     "Описание": f"{fourth_sign_params['Состояние газовой системы'][gas_condition]['name']} - {fourth_sign_params['Состояние газовой системы'][gas_condition]['desc']}",
     "Балл": fourth_sign_params['Состояние газовой системы'][gas_condition]['value'],
     "Итог": fourth_sign_params['Состояние газовой системы'][gas_condition]['value']},
    
    # Пятый знак
    {"Знак": 5, "Параметр": "Покраска придомовой территории", 
     "Код": painting_frequency, 
     "Описание": f"{fifth_sign_params['Покраска придомовой территории'][painting_frequency]['name']} - {fifth_sign_params['Покраска придомовой территории'][painting_frequency]['desc']}",
     "Балл": fifth_sign_params['Покраска придомовой территории'][painting_frequency]['value'],
     "Итог": fifth_sign_params['Покраска придомовой территории'][painting_frequency]['value']},
    {"Знак": 5, "Параметр": "Уход за придомовой зеленью", 
     "Код": greenery_care, 
     "Описание": f"{fifth_sign_params['Уход за придомовой зеленью'][greenery_care]['name']} - {fifth_sign_params['Уход за придомовой зеленью'][greenery_care]['desc']}",
     "Балл": fifth_sign_params['Уход за придомовой зеленью'][greenery_care]['value'],
     "Итог": fifth_sign_params['Уход за придомовой зеленью'][greenery_care]['value']},
    
    # Шестой знак
    {"Знак": 6, "Параметр": "Подготовка к праздникам", 
     "Код": holiday_preparation, 
     "Описание": f"{sixth_sign_params['Подготовка к праздникам'][holiday_preparation]['name']} - {sixth_sign_params['Подготовка к праздникам'][holiday_preparation]['desc']}",
     "Балл": sixth_sign_params['Подготовка к праздникам'][holiday_preparation]['value'],
     "Итог": sixth_sign_params['Подготовка к праздникам'][holiday_preparation]['value']}
]

# Создаём DataFrame и сохраняем в Excel
df = pd.DataFrame(data)
# Переупорядочиваем колонки, чтобы "Итог" была последней
columns_order = ['Знак', 'Параметр', 'Код', 'Описание', 'Балл', 'Итог']
df = df[columns_order]
excel_file = "building_characteristics.xlsx"
df.to_excel(excel_file, index=False, sheet_name="Характеристики")

# Выводим результат
print("\n=== Итоговые данные ===")
print(df)
print(f"\nФайл сохранён: {excel_file}")

# Выводим общий итоговый балл
total_score = sum(row['Итог'] for row in data if isinstance(row['Итог'], (int, float)))
print(f"\nОбщий итоговый балл: {total_score}")