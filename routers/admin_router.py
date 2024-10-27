from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from .command_router import UserState
from shared.funcs import get_user_status, get_start_keyboard, save_users, users, status_translation
from shared.config import user_state


admin_router = Router()


# Обробник введення Telegram ID для зміни статусу
@admin_router.message(UserState.waiting_for_user_id)
async def handle_user_id_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    target_user_id = message.text.strip()
    user_status = get_user_status(user_id)

    if target_user_id.isdigit() and int(target_user_id) in users:
        # user_state[user_id] = 'waiting_for_new_status'
        await state.set_state(UserState.waiting_for_new_status)
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
@admin_router.message(UserState.waiting_for_new_status)
async def handle_new_status_selection(message: Message, state: FSMContext):
    admin_id = message.from_user.id
    new_status = message.text.strip()
    target_user_id = user_state.get('target_user_id')

    if new_status in ["demo", "unlim", "admin"]:
        users[target_user_id]['status'] = new_status
        save_users(users)  # Зберігаємо зміни
        await message.answer(f"✅ Статус користувача з ID {target_user_id} змінено на {status_translation.get(new_status, new_status)}.", reply_markup=get_start_keyboard(admin_id))
        # user_state[admin_id] = 'waiting_for_start'
        await state.set_state(UserState.waiting_for_start)
    else:
        await message.answer("⚠️ Некоректний статус. Будь ласка, виберіть із запропонованих варіантів.")
