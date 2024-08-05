from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.users.lang import lang_dict


async def lang_keyboard():
    start_keyb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keybs = lang_dict.get('language')
    button = [KeyboardButton(text=f"{til}") for til in keybs.values()]
    start_keyb.add(*button)
    return start_keyb

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Bosh menyu"),
        ],
    ],
    resize_keyboard=True,
)
