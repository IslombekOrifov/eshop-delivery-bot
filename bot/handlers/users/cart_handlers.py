import os
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from loader import dp, db
from states.menuData import MenuData
from tashkent_time import get_tashkent_time

from handlers.users.lang import (
    get_lang_text, values_to_list
)
from keyboards.default.menu_keyboards import (
    main_menu_keyboard,
)

from keyboards.inline.cart_inline_keb import (
    clear_cart,
    rm_item,
    cart_keyboard,
)

from keyboards.inline.category_inline import (
    catagory_inline_keyboard,
)

image_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'site', 'media'))



@dp.message_handler(lambda message: message.text in values_to_list('cart') and message.content_type == types.ContentType.TEXT, state='*')
async def cart_menu(msg: types.Message, state: FSMContext):
    """Bu funksiya cartlar uchun"""
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        cart_data = await cart_keyboard(msg.from_user.id, lang_code)
        if cart_data['has_cart']:
            text = cart_data['text']
            products_price = cart_data['products_price']
            keyboard_markup = cart_data['keyboard']

            await state.update_data(
                {'amount': products_price}
            )
            text += f"{await get_lang_text('price_all_text', lang_code)}: {products_price} {await get_lang_text('price_currency_text', lang_code)}"
            await msg.answer(text=text, reply_markup=keyboard_markup)
        else:
            categories = await db.get_categories()
            markup_inline = await catagory_inline_keyboard(categories, lang_code, is_main=True)
            await msg.answer(text = await get_lang_text('empty_cart_text', lang_code))
            photo_path = os.path.join(image_directory, 'logo/logo.jpg')
            with open(photo_path, 'rb') as photo:
                await msg.answer_photo(photo=photo, reply_markup=markup_inline)
            await MenuData.MENU.set()
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.answer(text)

# Handler for subtracting an item
@dp.callback_query_handler(rm_item.filter(), state='*')
async def remove_cart_item_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    item_id = int(callback_data['cart_id'])
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        drop = await db.drop_cart_item(item_id)

        cart_data = await cart_keyboard(query.from_user.id, lang_code)        

        if cart_data['has_cart']:
            text = cart_data['text']
            products_price = cart_data['products_price']
            keyboard_markup = cart_data['keyboard']

            await state.update_data(
                {'amount': products_price}
            )
            text += f"{await get_lang_text('price_all_text', lang_code)}: {products_price} {await get_lang_text('price_currency_text', lang_code)}"
            await query.message.edit_text(text)
            await query.message.edit_reply_markup(reply_markup=keyboard_markup)
        else:
            categories = await db.get_categories()
            markup_inline = await catagory_inline_keyboard(categories, lang_code, is_main=True)
            await query.message.delete()
            await query.message.answer(text = await get_lang_text('empty_cart_text', lang_code))
            photo_path = os.path.join(image_directory, 'logo/logo.jpg')
            with open(photo_path, 'rb') as photo:
                await query.message.answer_photo(photo=photo, reply_markup=markup_inline)
            await MenuData.MENU.set()
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await query.message.delete()
        await query.message.answer(text)
        

# Handler for subtracting an item
@dp.callback_query_handler(clear_cart.filter(), state='*')
async def clear_cart_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    drop = await db.drop_all_cart_item(query.from_user.id)
    await state.update_data({'delivery_time': None})

    keyboard_markup = await main_menu_keyboard(lang_code)
    await query.message.delete()
    await query.message.answer(text = await get_lang_text('empty_cart_text', lang_code))
