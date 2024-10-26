from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Кнопки для вибору частоти
frequency_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Без затримки 🚀")],
        [KeyboardButton(text="1 заявка в 10 секунд ⏳")],
        [KeyboardButton(text="1 заявка в 10 хвилин ⌛")],
        [KeyboardButton(text="1 заявка в 60 хвилин ⌛")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Кнопки для вибору тривалості
demo_duration_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1 хвилина ⏳")],
        [KeyboardButton(text="15 хвилин ⏳")],
        [KeyboardButton(text="30 хвилин ⏳")],
        [KeyboardButton(text="1 година ⏳")],
        [KeyboardButton(text="3 години ⏳")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
admin_duration_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1 хвилина ⏳")],
        [KeyboardButton(text="15 хвилин ⏳")],
        [KeyboardButton(text="30 хвилин ⏳")],
        [KeyboardButton(text="1 година ⏳")],
        [KeyboardButton(text="3 години ⏳")],
        [KeyboardButton(text="Необмежено ⏳")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Кнопка зупинки відправки
stop_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зупинити відправку ❌")],
    ],
    resize_keyboard=True
)

# Кнопка для головного меню
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🤵 Профіль")],
        # [KeyboardButton(text="🚀 Запустити відправку заявок")],
        [KeyboardButton(text="🚀 Відправка заявок")],
        [KeyboardButton(text="🧑‍💻 Підтримка")],
        [KeyboardButton(text="🔘 Whitelist")],
    ],
    resize_keyboard=True
)

admin_start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🤵 Профіль")],
        # [KeyboardButton(text="🚀 Запустити відправку заявок")],
        [KeyboardButton(text="🚀 Відправка заявок")],
        [KeyboardButton(text="🧑‍💻 Підтримка")],
        [KeyboardButton(text="🔘 Whitelist")],
        [KeyboardButton(text="💠 Змінити статус")]
    ],
    resize_keyboard=True
)