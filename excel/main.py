import pandas as pd

# Базы данных характеристик
construction_periods = {
    "А": "Новостройки (после 2015)",
    "Б": "Современные (2000-2014)", 
    "В": "Типовые (1970-1999)",
    "Г": "Старые (1946-1969)",
    "Д": "Дореволюционные (до 1945)"
}

wall_materials = {
    "А": "Кирпичные",
    "Б": "Панельные",
    "В": "Монолитные", 
    "Г": "Деревянные",
    "Д": "Смешанные"
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
    }
}

def get_choice(options_dict, prompt, numeric=False):
    print(f"\n{prompt}:")
    
    if numeric and isinstance(next(iter(options_dict.values())), dict):
        for key, data in options_dict.items():
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

# Формируем данные для таблицы
data = [
    {"Знак": 1, "Параметр": "Период строительства", "Код": period, "Описание": construction_periods[period], "Балл": ""},
    {"Знак": 2, "Параметр": "Материал стен", "Код": material, "Описание": wall_materials[material], "Балл": ""},
    {"Знак": 3, "Параметр": "Этажность", 
     "Код": height, 
     "Описание": f"{third_sign_params['Этажность'][height]['name']} ({third_sign_params['Этажность'][height]['range']})",
     "Балл": third_sign_params['Этажность'][height]['value']},
    {"Знак": 3, "Параметр": "Лифты", 
     "Код": elevator, 
     "Описание": third_sign_params['Лифты'][elevator]['name'],
     "Балл": third_sign_params['Лифты'][elevator]['value']},
    {"Знак": 3, "Параметр": "Мусоропровод", 
     "Код": garbage, 
     "Описание": third_sign_params['Мусоропровод'][garbage]['name'],
     "Балл": third_sign_params['Мусоропровод'][garbage]['value']}
]

# Создаём DataFrame и сохраняем в Excel
df = pd.DataFrame(data)
excel_file = "building_characteristics.xlsx"
df.to_excel(excel_file, index=False, sheet_name="Характеристики")

# Выводим результат
print("\n=== Итоговые данные ===")
print(df[['Знак', 'Параметр', 'Описание', 'Балл']])
print(f"\nФайл сохранён: {excel_file}")