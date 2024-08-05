import asyncio
import os

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db
from states.menuData import MenuData

from handlers.users.lang import (
    get_lang_text, values_to_list
)
from keyboards.default.menu_keyboards import (
    main_menu_keyboard, 
)

image_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'site', 'media'))


@dp.message_handler(lambda message: message.text in values_to_list('back'), state='*')
async def back_without_state(msg: types.Message, state: FSMContext):
    """ bu funksiya tepadegi ikkita filter uchun ham ishlaydi."""
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    text = await get_lang_text('main_menu_text', lang_code)
    keyboard_markup = await main_menu_keyboard(lang_code)
    await msg.answer(text, reply_markup=keyboard_markup)
    await MenuData.MENU.set()