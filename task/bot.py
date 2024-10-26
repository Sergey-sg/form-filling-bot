import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from bs4 import BeautifulSoup
import random
import logging
from datetime import datetime
import time
from urllib.parse import urlsplit, urlunsplit, urlparse


from keyboards import frequency_keyboard, demo_duration_keyboard, admin_duration_keyboard, stop_keyboard, start_keyboard, admin_start_keyboard
from funcs import (generate_name,
                   generate_phone_number,
                   is_valid_url,
                   load_users_data,
                   get_user_status,
                   get_start_keyboard,
                   get_duration_keyboard,
                   is_valid_url_aiohttp,
                   load_users,
                   save_users,
                   register_user,
                   extract_domain,
                   is_demo_limit_reached,
                   users)
from funcs import status_translation

API_TOKEN = ''

# Дані проксі
USE_PROXY_1 = True
PROXY_IP_1 = ''
PROXY_PORT_1 = ''
PROXY_LOGIN_1 = ''
PROXY_PASSWORD_1 = ''

USE_PROXY_2 = True
PROXY_IP_2 = ''
PROXY_PORT_2 = ''
PROXY_LOGIN_2 = ''
PROXY_PASSWORD_2 = ''

USE_PROXY_3 = True
PROXY_IP_3 = ''
PROXY_PORT_3 = ''
PROXY_LOGIN_3 = ''
PROXY_PASSWORD_3 = ''

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальні змінні для зберігання стану бота
user_state = {}
user_urls = {}
user_request_counter = {}
user_durations = {}  # Тривалість для кожного користувача
user_frequencies = {}  # Частота для кожного користувача

# Файл для зберігання даних користувачів
USERS_FILE = 'users.json'


# Обробник команди /start
@dp.message(Command('start'))
async def start_handler(message: Message):
    user_id = message.from_user.id
    register_user(user_id)

    user_state[user_id] = 'waiting_for_start'
    await message.answer(
        '⚡️ Привіт! За допомогою цього боту ти можеш відправити заявки на будь які сайти з формою\n'
        '💎 Ми маємо різні режими з вибором тривалості та швидкості відправки заявок\n'
        '💡 Всі поля, випадаючі списки, галочки в формі на сайтах заповнюються автоматично\n'
        '🔥 Тисни кнопку нижче та запускай відправку!',
        reply_markup=get_start_keyboard(user_id)
    )

# Обробник кнопки "Змінити статус" для адмінів
@dp.message(lambda message: users.get(message.from_user.id, {}).get('status') == 'admin' and message.text == "💠 Змінити статус")
async def change_status_handler(message: Message):
    user_id = message.from_user.id
    user_state[user_id] = 'waiting_for_user_id'
    await message.answer("👤 Введіть Telegram ID користувача, якому хочете змінити статус:")


# Обробник введення Telegram ID для зміни статусу
@dp.message(lambda message: user_state.get(message.from_user.id) == 'waiting_for_user_id')
async def handle_user_id_input(message: Message):
    user_id = message.from_user.id
    target_user_id = message.text.strip()
    user_status = get_user_status(user_id)

    if target_user_id.isdigit() and int(target_user_id) in users:
        user_state[user_id] = 'waiting_for_new_status'
        user_state['target_user_id'] = int(target_user_id)
        await message.answer(
            f"🚦 Виберіть новий статус для користувача(Current Status:{user_status}):",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="demo")],
                    [KeyboardButton(text="unlim")],
                    [KeyboardButton(text="admin")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
    else:
        await message.answer("⚠️ Некоректний ID або користувач не знайдений. Введіть правильний Telegram ID.")

# Обробник вибору нового статусу для користувача
@dp.message(lambda message: user_state.get(message.from_user.id) == 'waiting_for_new_status')
async def handle_new_status_selection(message: Message):
    admin_id = message.from_user.id
    new_status = message.text.strip()
    target_user_id = user_state.get('target_user_id')

    if new_status in ["demo", "unlim", "admin"]:
        users[target_user_id]['status'] = new_status
        save_users(users)  # Зберігаємо зміни
        await message.answer(f"✅ Статус користувача з ID {target_user_id} змінено на {status_translation.get(new_status, new_status)}.", reply_markup=get_start_keyboard(admin_id))
        user_state[admin_id] = 'waiting_for_start'
    else:
        await message.answer("⚠️ Некоректний статус. Будь ласка, виберіть із запропонованих варіантів.")

# Обробник кнопки "Підтримка"
@dp.message(lambda message: message.text == "🧑‍💻 Підтримка")
async def support_handler(message: Message):
    await message.answer("✉️ Для звʼязку з нами звертайтеся до...")

# Обробник кнопки "Профіль"
@dp.message(lambda message: message.text == "🤵 Профіль")
async def profile_handler(message: Message):
    user_id = message.from_user.id
    user_data = users.get(user_id, {})
    registration_date = user_data.get('registration_date')
    status = user_data.get('status', 'N/A')
    translated_status = status_translation.get(status, status)
    total_applications_sent = user_data.get('applications_sent', 0)

    if registration_date:
        days_since_registration = (datetime.now() - datetime.fromisoformat(registration_date)).days
        await message.answer(
            f"<b>🤵 Ваш профіль</b>\n\n"
            f"📊 Ваш статус: {translated_status}\n"
            f"🪪 Ваш Telegram ID: <code>{user_id}</code>\n"
            f"🥇 Ми разом вже {days_since_registration} днів\n"
            f"📩 Загалом надіслано заявок: {total_applications_sent}",
            parse_mode='HTML'
        )
    else:
        await message.answer("⚠️ Ви не зареєстровані. Напишіть боту /start")

# Whitelist
@dp.message(lambda message: message.text == "🔘 Whitelist")
async def show_whitelist_menu(message: Message):
    user_id = message.from_user.id
    user_data = users.get(user_id, {})

    # Перевірка статусу користувача
    if user_data.get('status') == 'demo':
        await message.answer("❌ Ця функція доступна тільки у платній версії боту.")
        return

    whitelist_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Додати домен")],
            [KeyboardButton(text="Список доменів")],
            [KeyboardButton(text="Повернутися назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Вітаю у меню вайтлисту! Виберіть дію:", reply_markup=whitelist_keyboard)


@dp.message(lambda message: message.text == "Додати домен")
async def request_domain(message: Message):
    user_id = message.from_user.id
    user_data = users.get(user_id, {})
    user_domains = user_data.get('whitelist', [])

    # Перевірка статусу користувача
    if user_data.get('status') == 'demo':
        await message.answer("❌ Ця функція доступна тільки у платній версії боту.")
        return

    # Перевірка, чи користувач досяг ліміту на 3 домени
    if user_data.get('status') != 'admin' and len(user_domains) >= 3:
        await message.answer("❌ Ви не можете додати більше 3-х доменів.")
        return

    await message.answer("📩 Відправте посилання на сайт, домен якого ви хочете додати.")
    user_state[user_id] = 'waiting_for_domain'


@dp.message(lambda message: message.text == "Список доменів")
async def list_domains(message: Message):
    user_id = message.from_user.id
    user_data = users.get(user_id, {})
    user_domains = user_data.get('whitelist', [])

    if not user_domains:
        await message.answer("📋 Ваш вайтлист порожній.")
    else:
        # Створюємо клавіатуру для видалення доменів
        domain_buttons = []

        # Додаємо кнопки для кожного домену
        for domain in user_domains:
            domain_buttons.append([KeyboardButton(text=domain)])  # Кнопка для домену

        # Додаємо кнопку "Повернутися назад"
        domain_buttons.append([KeyboardButton(text="Повернутися назад")])

        # Формуємо клавіатуру
        domain_keyboard = ReplyKeyboardMarkup(
            keyboard=domain_buttons,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer("Виберіть домен, який хочете видалити:", reply_markup=domain_keyboard)

# Функція для обробки натискання на домен
@dp.message(lambda message: message.text in [domain for domain in users.get(message.from_user.id, {}).get('whitelist', [])])
async def delete_domain(message: Message):
    user_id = message.from_user.id
    domain_to_remove = message.text

    # Видаляємо домен з вайтлиста
    if domain_to_remove in users[user_id].get('whitelist', []):
        users[user_id]['whitelist'].remove(domain_to_remove)
        save_users(users)
        await message.answer(f"✅ Домен {domain_to_remove} видалено з вайтлиста.")
    else:
        await message.answer("❌ Домен не знайдено у вашому вайтлисті.")

    # Повертаємось до списку доменів
    await list_domains(message)

# Обробник кнопки "Повернутися назад"
@dp.message(lambda message: message.text == "Повернутися назад")
async def back_to_main_menu(message: Message):
    user_id = message.from_user.id
    user_state[user_id] = 'main_menu'  # Скидаємо стан користувача або встановлюємо на основний стан
    await message.answer("🔙 Ви повернулися в головне меню.", reply_markup=get_start_keyboard(user_id))


# Waiting fot domain
@dp.message(lambda message: user_state.get(message.from_user.id) == 'waiting_for_domain')
async def add_domain(message: Message):
    user_id = message.from_user.id
    user_domain = message.text

    # Отримуємо домен з URL
    domain = urlparse(user_domain).netloc
    if domain.startswith('www.'):
        domain = domain[4:]

    # Додаємо домен до користувача
    users[user_id]['whitelist'] = users[user_id].get('whitelist', [])
    if domain not in users[user_id]['whitelist']:
        users[user_id]['whitelist'].append(domain)
        save_users(users)  # Зберегти оновлення
        await message.answer(f"✅ Домен {domain} успішно додано до вайтлиста.")
    else:
        await message.answer("❌ Цей домен вже додано до вайтлиста.")

    # Повертаємося до меню вайтлиста
    await show_whitelist_menu(message)

# Обробник кнопки "Запустити відправку заявок"
@dp.message(lambda message:
    (user_state.get(message.from_user.id) == 'waiting_for_start' or user_state.get(message.from_user.id) == 'main_menu')
    and message.text == "🚀 Запустити відправку заявок")
async def initiate_request(message: Message):
    user_id = message.from_user.id
    logger.info(f"Користувач {user_id} натиснув кнопку 'Запустити відправку заявок'")

    user_data = users.get(user_id, {})
    applications_sent = user_data.get('applications_sent', 0)

    # Перевірка ліміту лише для статусу demo
    if user_data.get('status') == 'demo' and is_demo_limit_reached(user_id):
        await message.answer("❌ Ви вже досягли ліміту в 50 заявок. Для отримання повного доступу зверніться до адміністратора.")
        return

    # Визначити скільки заявок потрібно відправити
    if user_data.get('status') == 'demo':
        requests_to_send = 50 - applications_sent
        if requests_to_send <= 0:
            await message.answer("❌ Ви вже досягли ліміту в 50 заявок. Для отримання повного доступу зверніться до адміністратора.")
            return
        await message.answer(f'🌐 Ви можете надіслати ще до {requests_to_send} заявок. Введіть посилання на сайт:')
    else:
        await message.answer('🌐 Введіть посилання на сайт:')

    user_state[user_id] = 'waiting_for_url'


# Обробник повторного введення посилання на сайт
@dp.message(lambda message: user_state.get(message.from_user.id) == 'waiting_for_url')
async def handle_url(message: Message):
    url = message.text
    user_id = message.from_user.id
    domain = extract_domain(url)  # Реалізуйте цю функцію для отримання домену з URL

    # Перевірка, чи існує домен у вайтлісті інших користувачів
    for uid, data in users.items():
        if 'whitelist' in data and domain in data['whitelist']:
            await message.answer(f"❌ Домен '{domain}' вже існує у вайтлісті іншого користувача. Будь ласка, введіть інший домен.")
            return

    # Перевірка валідності URL
    if is_valid_url(url):
        user_urls[user_id] = url
        user_state[user_id] = 'waiting_for_frequency'
        await message.answer("🕰 Як швидко будуть відправлятися заявки?", reply_markup=frequency_keyboard)
    else:
        await message.answer("⚠️ Будь ласка, введіть коректне посилання на сайт")


# Обробник вибору тривалості
@dp.message(lambda message: user_state.get(message.from_user.id) in ['waiting_for_frequency', 'waiting_for_duration'] and
              message.text in ["Без затримки 🚀", "1 заявка в 10 секунд ⏳", "1 заявка в 10 хвилин ⌛", "1 заявка в 60 хвилин ⌛",
                               "1 хвилина ⏳", "15 хвилин ⏳", "30 хвилин ⏳", "1 година ⏳", "3 години ⏳", "Необмежено ⏳"])
async def handle_frequency_and_duration(message: Message):
    user_id = message.from_user.id
    user_data = users.get(user_id, {})

    # Обробка вибору частоти
    if user_state[user_id] == 'waiting_for_frequency':
        frequency = message.text
        user_frequencies[user_id] = frequency

        # Якщо статус "demo", обираємо частоту, ігноруємо тривалість
        if user_data.get('status') == 'demo':
            user_state[user_id] = 'active'
            await message.answer("💫 Частота обрана. Вибір тривалості відправки заявок у демо статусі недоступний.")
            website_url = user_urls[user_id]
            await message.answer(f"🚀 Космічний шатл з купою заявок вже летить на сайт: {website_url}", reply_markup=stop_keyboard)
            asyncio.create_task(request_loop(user_id, frequency, duration=None))  # Демо: тривалість None (без обмежень)
            return

        # Для інших статусів
        user_state[user_id] = 'waiting_for_duration'
        await message.answer("⏳ Як довго будуть відправлятися заявки?", reply_markup=get_duration_keyboard(user_id))
        return

    # Обробка вибору тривалості
    if user_state[user_id] == 'waiting_for_duration':
        duration_mapping = {
            "1 хвилина ⏳": 60,
            "15 хвилин ⏳": 15 * 60,
            "30 хвилин ⏳": 30 * 60,
            "1 година ⏳": 60 * 60,
            "3 години ⏳": 3 * 60 * 60,
            "Необмежено ⏳": None  # Необмежена тривалість
        }

        # Пропускаємо демо-статус для тривалості
        if user_data.get('status') != 'demo':
            user_durations[user_id] = duration_mapping[message.text]

        # Підготовка до запуску відправки заявок
        frequency = user_frequencies[user_id]
        user_state[user_id] = 'active'
        website_url = user_urls[user_id]
        await message.answer(f"🚀 Космічний шатл з купою заявок вже летить на сайт: {website_url}", reply_markup=stop_keyboard)

        # Запуск request_loop з вказаною тривалістю
        asyncio.create_task(request_loop(user_id, frequency, duration=user_durations.get(user_id)))

# Обробник вибору частоти
async def send_requests(user_id, frequency):
    delay_mapping = {
        "Без затримки 🚀": 0,
        "1 заявка в 10 секунд ⏳": 10,
        "1 заявка в 10 хвилин ⌛": 600,
        "1 заявка в 60 хвилин ⌛": 3600
    }

    delay = delay_mapping.get(frequency, 0)

    # Формування проксі
    proxies = []
    if USE_PROXY_1:
        proxy_1 = f"http://{PROXY_LOGIN_1}:{PROXY_PASSWORD_1}@{PROXY_IP_1}:{PROXY_PORT_1}"
        proxies.append(proxy_1)
    if USE_PROXY_2:
        proxy_2 = f"http://{PROXY_LOGIN_2}:{PROXY_PASSWORD_2}@{PROXY_IP_2}:{PROXY_PORT_2}"
        proxies.append(proxy_2)
    if USE_PROXY_3:
        proxy_3 = f"http://{PROXY_LOGIN_3}:{PROXY_PASSWORD_3}@{PROXY_IP_3}:{PROXY_PORT_3}"
        proxies.append(proxy_3)

    attempts = 3  # Загальна кількість спроб

    for attempt in range(attempts):
        proxy_url = random.choice(proxies) if proxies else None
        logger.info(f"Використання запиту з проксі: {proxy_url}" if proxy_url else "Використання запиту без проксі.")

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                logger.info(f"Надсилаємо GET запит до: {user_urls[user_id]}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
                }

                async with session.get(user_urls[user_id], proxy=proxy_url, headers=headers) as response:
                    logger.info(f"Отримано відповідь: {response.status}")
                    if response.status != 200:
                        if attempt < attempts - 1:  # Якщо це не остання спроба
                            logger.warning("Сайт недоступний. Спробуємо ще раз...")
                            await asyncio.sleep(10)  # Затримка перед повтором
                            continue  # Повертаємось до початку циклу
                        return f"Сайт недоступний. Код статусу: {response.status}."

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    form = soup.find('form')

                    if not form:
                        return "Форма не знайдена."

                    action = form.get('action')
                    if action:
                        if not action.startswith('http'):
                            base_url = user_urls[user_id]
                            split_url = urlsplit(base_url)
                            base_url_without_query = urlunsplit((split_url.scheme, split_url.netloc, split_url.path.rstrip('/') + '/', '', ''))
                            action = f"{base_url_without_query}{action.lstrip('/')}"

                        logger.info(f"Формований URL дії: {action}")

                    data = {}
                    inputs = form.find_all('input')
                    for input_tag in inputs:
                        input_name = input_tag.get('name')
                        input_type = input_tag.get('type')

                        if input_type == 'name' or input_name == 'name':
                            data[input_name] = generate_name()

                        elif input_type == 'tel' or input_name == 'phone' or input_name == 'tel':
                            data[input_name] = generate_phone_number()

                        elif input_type == 'checkbox':
                            data[input_name] = 'on'

                    selects = form.find_all('select')
                    for select in selects:
                        select_name = select.get('name')
                        options = select.find_all('option')
                        valid_options = [option for option in options if option.get('value')]
                        if valid_options:
                            selected_option = random.choice(valid_options).get('value')
                            data[select_name] = selected_option

                    logger.info(f"Дані, які будуть надіслані: {data}")

                    for post_attempt in range(attempts):
                        async with session.post(action, data=data, proxy=proxy_url) as post_response:
                            if post_response.status == 200:
                                logger.info(f"Запит на {action} успішно надіслано.")
                                user_request_counter[user_id] += 1
                                return None  # Успішно відправлено
                            else:
                                logger.error(f"Помилка при відправці: {post_response.status}")
                                if post_attempt < attempts - 1:  # Якщо це не остання спроба
                                    await asyncio.sleep(10)  # Затримка 10 секунд перед повтором
                                else:
                                    return "Не вдалося відправити заявку."

            except aiohttp.ClientError as e:
                logger.error(f"Помилка при використанні проксі: {e}")
                if attempt < attempts - 1:  # Якщо це не остання спроба
                    await asyncio.sleep(10)  # Затримка 10 секунд перед повтором
                else:
                    return "Проблема з проксі."

    return None  # Успішно відправлено


async def request_loop(user_id, frequency, duration):
    user_request_counter[user_id] = 0  # Скинути лічильник
    delay_mapping = {
        "Без затримки 🚀": 0,
        "1 заявка в 10 секунд ⏳": 10,
        "1 заявка в 10 хвилин ⌛": 600,
        "1 заявка в 60 хвилин ⌛": 3600
    }

    delay = delay_mapping.get(frequency, 0)
    user_data = users[user_id]

    # Якщо статус demo, кількість заявок для відправки обмежується
    requests_to_send = 50 - user_data['applications_sent'] if user_data.get('status') == 'demo' else float('inf')

    # Обчислити час закінчення, якщо тривалість обмежена
    end_time = None
    if duration is not None:
        end_time = time.time() + duration

    while user_state.get(user_id) == 'active' and requests_to_send > 0:
        # Перевірка на обмеження за часом
        if end_time is not None and time.time() >= end_time:
            break

        error_message = await send_requests(user_id, frequency)
        if error_message:
            await bot.send_message(user_id, f"❌ {error_message}")
            user_state[user_id] = 'waiting_for_start'
            await bot.send_message(user_id, "⬇️ Використовуйте кнопку нижче:", reply_markup=start_keyboard)
            break

        if user_data.get('status') == 'demo':
            requests_to_send -= 1

        logger.info(f"Затримка перед наступним запитом: {delay} секунд.")
        await asyncio.sleep(delay)

    if user_state.get(user_id) == 'active':
        user_state[user_id] = 'waiting_for_start'
        users[user_id]['applications_sent'] += user_request_counter[user_id]  # Оновити загальний лічильник
        save_users(users)  # Зберегти оновлення
        await bot.send_message(user_id,
                               f"✅ Відправка заявок завершена\n✉️ Всього відправлено заявок: {user_request_counter[user_id]}",
                               reply_markup=start_keyboard)

# Обробник зупинки
@dp.message(lambda message: user_state.get(message.from_user.id) == 'active' and message.text == "Зупинити відправку ❌")
async def stop_sending(message: Message):
    user_id = message.from_user.id
    user_state[user_id] = 'waiting_for_start'
    total_requests = user_request_counter.get(user_id, 0)

    # Оновлення загальної кількості заявок у users.json
    if user_id in users:
        users[user_id]['applications_sent'] += total_requests
        save_users(users)

    await message.answer(f"⭕️ Відправка заявок зупинена\n✉️ Всього відправлено заявок: {total_requests}", reply_markup=get_start_keyboard(user_id))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
