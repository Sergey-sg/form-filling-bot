from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime

from shared.funcs import get_start_keyboard, register_user, users
from shared.data import status_translation

commands_router = Router()

class UserState(StatesGroup):
    waiting_for_start = State()
    waiting_for_user_id = State()
    waiting_for_new_status = State()
    waiting_for_domain = State()
    waiting_for_url = State()
    waiting_for_frequency = State() 
    waiting_for_duration = State()
    main_menu = State()


# Обробник команди /start
@commands_router.message(Command('start'))
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    register_user(user_id)
    await state.set_state(UserState.waiting_for_start)
    await message.answer(
        '⚡️ Привіт! За допомогою цього боту ти можеш відправити заявки на будь які сайти з формою\n'
        '💎 Ми маємо різні режими з вибором тривалості та швидкості відправки заявок\n'
        '💡 Всі поля, випадаючі списки, галочки в формі на сайтах заповнюються автоматично\n'
        '🔥 Тисни кнопку нижче та запускай відправку!',
        reply_markup=get_start_keyboard(user_id)
    )

# Обробник кнопки "Підтримка"
@commands_router.message(lambda message: message.text == "🧑‍💻 Підтримка")
async def support_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✉️ Для звʼязку з нами звертайтеся до...")

# Обробник кнопки "Профіль"
@commands_router.message(lambda message: message.text == "🤵 Профіль")
async def profile_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
    user_data = users.get(user_id, {})
    registration_date = user_data.get('registration_date')
    status = user_data.get('status', 'N/A')
    translated_status = status_translation.get(status, status)
    total_applications_sent = user_data.get('applications_sent', 0)

    if registration_date:
        days_since_registration = (
            datetime.now() - datetime.fromisoformat(registration_date)).days
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

@commands_router.message(lambda message: message.text == "🚀 Відправка заявок" or message.text == "🚀 Меню заявок")
async def start_requesting(message: Message, state: FSMContext):
    await state.set_state(UserState.main_menu)
    buttons = [
        [InlineKeyboardButton(text="🚀 Запустити відправку заявок", callback_data="start_requesting")],
        [InlineKeyboardButton(text="📋 Активні сесії", callback_data="list_domains")],
    ]
    await message.answer("Оберіть опцію:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    
# Whitelist
@commands_router.message(lambda message: message.text == "🔘 Whitelist")
async def show_whitelist_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
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

# Обробник кнопки "Повернутися назад"
@commands_router.message(lambda message: message.text == "Повернутися назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Скидаємо стан користувача або встановлюємо на основний стан
    await state.set_state(UserState.main_menu)
    await message.answer("🔙 Ви повернулися в головне меню.", reply_markup=get_start_keyboard(user_id))

# Обробник кнопки "Змінити статус" для адмінів
@commands_router.message(lambda message: users.get(message.from_user.id, {}).get('status') == 'admin' and message.text == "💠 Змінити статус")
async def change_status_handler(message: Message, state: FSMContext):
    await state.set_state(UserState.waiting_for_user_id)
    await message.answer("👤 Введіть Telegram ID користувача, якому хочете змінити статус:")