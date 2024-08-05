from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp

from handlers.users.lang import (
    get_lang_text,
)
from keyboards.default.menu_keyboards import (
    main_menu_keyboard, 
)
from states.menuData import MenuData


# Echo bot
@dp.message_handler(state=None)
async def bot_echo(msg: types.Message, state: FSMContext):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    text = await get_lang_text('main_menu_text', lang_code)
    keyboard_markup = await main_menu_keyboard(lang_code)
    await msg.answer(text, reply_markup=keyboard_markup)
    await MenuData.MENU.set()
