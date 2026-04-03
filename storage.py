import json
import os

DATA_FILE = "wallets.json"

def save_balance(balance_dict: dict) -> None:
    """Сохраняет словарь балансов в JSON файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(balance_dict, f, indent=2, ensure_ascii=False)
        print(f" Данные сохранены в {DATA_FILE}")
    except Exception as e:
        print(f" Ошибка сохранения: {e}")

def load_balance() -> dict:
    """Загружает словарь балансов из JSON файла"""
    if not os.path.exists(DATA_FILE):
        print(f" Файл {DATA_FILE} не найден, создан новый словарь")
        return {}
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f" Загружено {len(data)} кошельков из {DATA_FILE}")
        return data
    except Exception as e:
        print(f" Ошибка загрузки: {e}")
        return {}