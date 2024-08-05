from environs import Env
from aiogram import types
import asyncpg

from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext

from keyboards.default.start_keyboard import lang_keyboard
from states.menuData import MenuData
from loader import dp, db
from data.config import ADMINS, SUPERUSERS

env = Env()
env.read_env()


@dp.message_handler(CommandStart(), chat_id=ADMINS)
async def admin_start(message: types.Message, state: FSMContext):
    await message.answer(f"Salom, {message.from_user.full_name}!")

@dp.message_handler(CommandStart(), chat_id=SUPERUSERS)
async def superuser_start(message: types.Message, state: FSMContext):
    await message.answer(f"Salom, {message.from_user.full_name}!")

@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    try:
        user = await db.add_user(
            username=message.from_user.username,
            telegram_id=message.from_user.id,
            language='ru',
        )
    except asyncpg.exceptions.UniqueViolationError:
        user = await db.select_user(telegram_id=message.from_user.id)
    keyboard = await lang_keyboard()
    text = f"Salom, {message.from_user.full_name}. Tilni tanlang!\n"
    text += f"Здравствуйте, {message.from_user.full_name}. Выберите язык!\n"
    await message.answer(text, reply_markup=keyboard)
    await MenuData.LANG_MENU.set()



    