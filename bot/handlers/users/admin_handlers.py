from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.utils import exceptions
import asyncio
import aiohttp


from data.config import ADMINS, IP
from loader import dp, db

from states.menuData import AdminData
from handlers.users.lang import lang_dict
from handlers.users.lang import (
    get_lang_sinc_args_text
)
from keyboards.inline.admin_checkout_inline_keyb import (
    check_status,
    order_confirm,
    order_reject,
    admin_checkout_keyboard,
)
from keyboards.inline.admin_checkout_inline_keyb import (
    delivered,
    delivered_keyboard,
)



@dp.callback_query_handler(order_confirm.filter(), state='*')
async def admin_order_confirm_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    order_id = int(callback_data.get('order_id'))
    client_id = int(callback_data.get('client'))
    lang_code = callback_data.get('lang_code')
    
    await db.update_order_status("process", order_id)
    
    keyboard = await delivered_keyboard(order_id, client_id, lang_code)
    await query.message.edit_reply_markup(reply_markup=keyboard)

    user_text = get_lang_sinc_args_text('order_preparing_text', lang_code, order_id)
    await dp.bot.send_message(client_id, user_text)
    

@dp.callback_query_handler(delivered.filter(), state='*')
async def order_delivered_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    order_id = int(callback_data.get('order_id'))
    client_id = callback_data.get('client')
    lang_code = callback_data.get('lang_code')
    await query.answer(cache_time=10)
    await query.message.edit_reply_markup(reply_markup=None)
    await db.update_order_status("delivered", order_id)
    user_text = get_lang_sinc_args_text('order_delivered_text', lang_code, order_id)
    await dp.bot.send_message(client_id, user_text)


@dp.callback_query_handler(check_status.filter(), state='*')
async def admin_order_check_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    order_id = int(callback_data.get('order_id'))
    client_id = int(callback_data.get('client'))
    lang_code = callback_data.get('lang_code')
    order = await db.get_order_only(order_id)
    if order['is_paid'] == False and order['status'] == 'rejected':
        keyboard = await admin_checkout_keyboard(order_id, client_id, lang_code)
        await query.message.delete_reply_markup()
    elif order['is_paid']:
        keyboard = await admin_checkout_keyboard(order_id, client_id, lang_code)
        await query.message.edit_reply_markup(reply_markup=keyboard)


@dp.callback_query_handler(order_reject.filter())
async def admin_order_reject_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    await query.message.delete_reply_markup()
    not_user_text = "❌❌❌\n" + query.message.text + "\n❌❌❌"
    await query.message.edit_text(not_user_text)
    order_id = int(callback_data.get('order_id'))
    client_id = int(callback_data.get('client'))
    lang_code = callback_data.get('lang_code')
    order = await db.update_order_status('rejected', order_id)
    text = get_lang_sinc_args_text('order_rejected_text', lang_code, order_id)
    await dp.bot.send_message(client_id, text)
    transaction = await db.get_transaction_only(int(order_id))
    if transaction:
        new_message = await click_cancel_order(transaction['id'], transaction)
        if new_message:
            await query.message.answer(text=new_message)
    
@dp.message_handler(content_types=types.ContentType.PHOTO, state=AdminData.ADVERTISING)
async def advertising_to_users(msg: types.Message, state: FSMContext):
    await state.finish()
    users = await db.get_users_telegram_id()
    caption = msg.caption if msg.caption else ""
    for user in users:
        user_id = user['telegram_id']
        try:
            await dp.bot.send_photo(user_id, photo=msg.photo[-1].file_id, caption=caption)
        except exceptions.BotBlocked:
            pass
        except exceptions.ChatNotFound:
            pass
        except exceptions.UserDeactivated:

            pass
        except exceptions.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
            await dp.bot.send_photo(user_id, photo=msg.photo[-1].file_id, caption=caption)


async def click_cancel_order(transaction_id):
    server_ip = IP
    url = f"http://{server_ip}/click/service/cancel_payment/"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "transaction_id": transaction_id,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                return "Buyurtma click tizimidan bekor qilindi"
            else:
                return "Xatolik mavjud"