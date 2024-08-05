import asyncio
import os

from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from data.config import ADMINS


from loader import dp, db
import logging
from tashkent_time import get_tashkent_time

from states.menuData import MenuData
from keyboards.default.start_keyboard import lang_keyboard
from keyboards.default.menu_keyboards import (
    main_menu_keyboard,
    create_back_keyboard,
)

from handlers.users.lang import (
    lang_dict, get_lang_key_by_value, 
    get_lang_text, menu_depart_to_list,
    elements_to_list, get_lang_sinc_text,
    get_lang_sinc_args_text
)

from keyboards.inline.category_inline import (
    category_item,
    fillial_item,
    catagory_inline_keyboard,
    products_inline_keyboard,
    fillials_inline_keyboard
)


image_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'site', 'media'))


@dp.message_handler(lambda message: message.text in lang_dict['language'].values(), state=MenuData.LANG_MENU)
async def set_lang_menu(msg: types.Message, state: FSMContext):
    """Bu funksiya tanlangan tilni xotiraga yozadi."""
    lang_code = await get_lang_key_by_value(lang_dict, msg.text)
    text = lang_dict.get('chenged_lang_text').get(lang_code)
    keyboards_markup = await main_menu_keyboard(lang_code)
    await msg.answer(text, reply_markup=keyboards_markup)
    await MenuData.MENU.set()
    await state.update_data({'lang': lang_code})
    await db.update_user_language(lang_code, msg.from_user.id)


@dp.message_handler(lambda message: message.text in elements_to_list('main_menu'), state='*')
async def all_menu_handler(msg: types.Message, state: FSMContext):
    """bu funksiya asosiy menyularni ushlab olish uchun ishlaydi."""
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    await state.finish()
    await MenuData.MENU.set()
    await state.update_data({'lang': lang_code})
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):

        text = None
        keyboard_markup = None

        if lang_code is None:
            user = await db.get_user(msg.from_user.id)
            if user:
                lang_code = user['language']
            else:
                lang_code = user['language']
            await state.update_data({'lang': lang_code})
        if msg.text == await menu_depart_to_list(lang_code, 0):
            # current_time = get_tashkent_time()
            # if (9 <= current_time.hour < 21) or (current_time.hour == 21 and current_time.minute <= 15):
            text = await get_lang_text('category_text', lang_code)
            categories = await db.get_categories()
            markup_inline = await catagory_inline_keyboard(categories, lang_code, is_main=True)
            photo_path = os.path.join(image_directory, 'logo/logo.jpg')
            with open(photo_path, 'rb') as photo:
                await msg.answer_photo(photo=photo, reply_markup=markup_inline)
            await MenuData.MENU.set()
            return
            # else:
                # text = await get_lang_text('restaurant_closed', lang_code)
                # await msg.answer(text)
        elif msg.text == await menu_depart_to_list(lang_code, 1):
            await old_order_menu(msg, state, lang_code)
        elif msg.text == await menu_depart_to_list(lang_code, 3):
            text = await get_lang_text('comments_text', lang_code)
            keyboard_markup = await create_back_keyboard(lang_code)
            await MenuData.COMMENT_MENU.set()
        elif msg.text == await menu_depart_to_list(lang_code, 4):
            fillials = await db.get_fillials()
            if fillials:
                new_markup = await fillials_inline_keyboard(fillials, lang_code)
                text = await get_lang_text('fillial_text', lang_code)
                await dp.bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
                await msg.answer(text, reply_markup=new_markup)
                # await msg.answer_location(latitude=41.334427, longitude=69.312733)
        elif msg.text == await menu_depart_to_list(lang_code, 5):
            text = await get_lang_text('chenge_lang_text', lang_code)
            keyboard_markup = await lang_keyboard()
            await MenuData.LANG_MENU.set()
        
        if text and keyboard_markup:
            await dp.bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
            await msg.answer(text, reply_markup=keyboard_markup)
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.answer(text)     


async def old_order_menu(msg: types.Message, state: FSMContext, lang_code):
    """ bu funksiya mijozning oxirgi 5 ta buyurtmasini ko'rsatish uchun."""
    orders = await db.get_delivered_or_rejected_orders(msg.from_user.id)
    lang_code = lang_code
    if orders:
        orders_count = orders[0]['total_orders_count']
        await msg.answer(get_lang_sinc_args_text("orders_count_text", lang_code, orders_count))
        for order in orders:
            if order['is_pick_up']:  
                text = get_lang_sinc_args_text('order_number_get_text', lang_code, order['id'], get_lang_sinc_text(order['status'], lang_code), order['address'])
            else:
                text = get_lang_sinc_args_text('order_number_text', lang_code, order['id'], get_lang_sinc_text(order['status'], lang_code), order['address'])
            amount = order['amount']
            items = await db.get_order_items(order['id'])
            title = f"title_{lang_code}"
            products_price = 0
            for item in items:
                product = await db.get_product_by_id(item['product_id'])
                text += f"{product[title]} {item['price']}/{item['org_measure']} x {item['quantity']}/{item['measure']}\n"
                products_price += item['quantity'] * item['price'] / item['org_count_in_measure']
            payment_text = "Click" if order['payment_click'] else get_lang_sinc_text("order_payment_type_cash_text", lang_code)
            
            delivery_fee = order['delivery_amount']
            
            delivery_fee_text = get_lang_sinc_text("delivery_fee_free", lang_code) if delivery_fee == 0 else str(35000) + get_lang_sinc_text("sum", lang_code)
            if order["is_pick_up"]:
                text += get_lang_sinc_args_text("order_payment_get_text", lang_code, payment_text, products_price, amount)
            else:
                text += get_lang_sinc_args_text("order_payment_text", lang_code, payment_text, products_price, delivery_fee_text, amount)

            await msg.answer(text)
    else:
        text = await get_lang_text('no_order_text', lang_code)
        await msg.answer(text)


@dp.message_handler(state=[MenuData.COMMENT_MENU, MenuData.MENU])
async def comment_menu(msg: types.Message, state: FSMContext):
    """Bu funksiya Kommentariyalar uchun"""
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        await MenuData.MENU.set()
        keyboards_markup = await main_menu_keyboard(lang_code)
        text = await get_lang_text('comments_recieved_text', lang_code)
        await msg.answer(text=text, reply_markup=keyboards_markup)
        for admin in ADMINS:
            try:
                await dp.bot.send_message(admin, f"Клиент: -> {msg.from_user.first_name}\nоставил(a) комментарий.\n\n{msg.text}")
            except Exception as err:
                logging.exception(err)
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.answer(text)


@dp.callback_query_handler(category_item.filter(), state=MenuData.MENU)
async def subcat_item_inline_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    cat_id = callback_data['cat_id']    
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
    
        category = await db.get_category(int(cat_id))
        child_type = "cat" if category['parent_id'] else "main_cat"

        parent_id = "0" if child_type == "main_cat" else category['parent_id']
        sub_category = await db.get_subcategories(int(cat_id))
        if sub_category:
            new_markup = await catagory_inline_keyboard(sub_category, lang_code, parent_id=parent_id, child_type=child_type)
            text = await get_lang_text('category_text', lang_code)
        else:
            products = await db.get_products(int(cat_id))
            if products:
                new_markup = await products_inline_keyboard(products, lang_code, parent_id=parent_id, child_type=child_type)
                text = await get_lang_text('category_text', lang_code)
        if sub_category or products:
            category = await db.get_category(int(cat_id))
            photo_path = os.path.join(image_directory, category['image'])
            with open(photo_path, 'rb') as photo:
                if query.message.photo:
                    await query.message.edit_media(media=types.InputMediaPhoto(photo), reply_markup=new_markup)
                else:
                    await query.message.delete()
                    await query.message.answer_photo(photo=photo, reply_markup=new_markup)
        await query.answer(cache_time=0)    
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await query.message.delete()
        await query.message.answer(text)

    
@dp.callback_query_handler(fillial_item.filter(), state="*")
async def fillial_detail_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    """This function is for fillial details"""
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    
    fill_id = callback_data['fill_id']
    item = await db.get_fillial_only(int(fill_id))
    if not item:
        return
    text = item['name'] + "\n\n" + await get_lang_text('address_text', lang_code) + item['address']
    await query.message.answer(text)
    await query.message.answer_location(latitude=item['latitude'], longitude=item['longitude'])
    await query.answer(cache_time=0)

    
