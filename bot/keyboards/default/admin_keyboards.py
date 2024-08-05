from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from loader import db

from handlers.users.lang import lang_dict, get_lang_text



admin_main_menu = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text='Buyurtmalar',),
            KeyboardButton(text='Yetkazib beruvchilar'),
        ],
    ],
    resize_keyboard=True,
)

back_menu = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text='Назад',),
        ],
    ],
    resize_keyboard=True,
)

async def main_menu_keyboard(lang_code):
    menu_keyb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keybs = lang_dict.get('main_menu').get(lang_code)
    button = (KeyboardButton(text=f"{menu}") for menu in keybs)
    menu_keyb.add(*button)
    return menu_keyb


async def create_back_keyboard(lang_code):
    back_keyb = ReplyKeyboardMarkup(resize_keyboard=True)
    back = await get_lang_text('back', lang_code)
    back_keyb.add(KeyboardButton(text=f"{back}"))
    return back_keyb