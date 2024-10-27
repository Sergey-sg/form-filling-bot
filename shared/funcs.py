
import aiohttp
import random
import phonenumbers
import re
import json
import tldextract
from datetime import datetime

from .keyboards import demo_duration_keyboard, admin_duration_keyboard, start_keyboard, admin_start_keyboard
from .data import ukrainian_names, operators
from .config import USERS_FILE


# Функція для генерації випадкового українського імені
def generate_name():
    return random.choice(ukrainian_names)

# Функція для генерації українського номера телефону з кодом оператора
def generate_phone_number():
    operator_name = random.choice(list(operators.keys()))
    operator_code = random.choice(operators[operator_name])
    phone_number = phonenumbers.parse(f"+380{operator_code}{random.randint(1000000, 9999999)}", None)
    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

# Функція для перевірки коректності URL
def is_valid_url(url):
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  
        r'localhost|'  
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  
        r'(?::\d+)?'  
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(url_pattern, url) is not None

# Завантаження даних користувачів з JSON-файлу
def load_users_data(filepath='users.json'):
    try:
        with open(filepath, 'r') as file:
            users = json.load(file)
        return users
    except FileNotFoundError:
        return {}

def get_user_status(user_id):
    users = load_users_data()
    user_data = users.get(str(user_id))
    if user_data:
        return user_data.get('status')
    return None

# Функція для визначення клавіатури
def get_start_keyboard(user_id):
    users = load_users_data()  # Завантажуємо дані користувачів
    if users.get(str(user_id), {}).get('status') == 'admin':
        return admin_start_keyboard
    return start_keyboard

def get_duration_keyboard(user_id):
    users = load_users_data()  # Завантажуємо дані користувачів
    if users.get(str(user_id), {}).get('status') == 'admin':
        return admin_duration_keyboard
    return demo_duration_keyboard

# Альтернативна асинхронна перевірка URL за допомогою aiohttp
async def is_valid_url_aiohttp(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return response.status == 200
    except aiohttp.ClientError:
        return False

# Завантаження даних користувачів з файлу
def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            users = json.load(file)
            return {int(user_id): user_data for user_id, user_data in users.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Збереження даних користувачів до файлу
def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# Ініціалізація користувачів
users = load_users()

# Додавання нового користувача
def register_user(user_id):
    if user_id not in users:
        users[user_id] = {
            'id': user_id,
            'registration_date': str(datetime.now()),
            'status': 'demo',
            'applications_sent': 0,
            'applications_per_url': {}
        }
        save_users(users)
def extract_domain(url: str) -> str:
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    return domain

# Назви статусів
status_translation = {
    'demo': 'Демо',
    'unlim': 'Необмежений',
    'admin': 'Адміністратор'
}

# Функція для перевірки чи користувач досяг ліміту заявок
def is_demo_limit_reached(user_id):
    user_data = users.get(user_id, {})
    return user_data.get('status') == 'demo' and user_data.get('applications_sent', 0) >= 50