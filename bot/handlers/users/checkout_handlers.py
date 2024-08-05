from environs import Env
import re
import os
import logging
import aiohttp
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from geopy.geocoders import Nominatim

from data.config import ADMINS, SUPERUSERS, IP
from loader import dp, db
from states.menuData import MenuData
from tashkent_time import get_tashkent_time

from handlers.users.lang import (
    get_lang_text, two_keys_to_list, payment_list,
    get_lang_sinc_text, get_lang_sinc_args_text,
    elements_to_list
)

from keyboards.default.menu_keyboards import main_menu_keyboard
from keyboards.inline.admin_checkout_inline_keyb import (
    admin_checkout_keyboard, admin_checkout_payment_keyboard
)
from keyboards.inline.cart_inline_keb import pre_checkout
from keyboards.default.checkout_keyboards import (
    ask_contact_keyboard, ask_location_keyboard,
    confirm_location_keyboard, payment_keyboard,
    fillial_keyboard, universal_keyboard
)


env = Env()
env.read_env()


PHONE_EXP = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
image_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'site', 'media'))


@dp.callback_query_handler(pre_checkout.filter(), state='*')
async def pre_checkout_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        
        user = await db.get_user(query.from_user.id)
        keyboard_markup = await ask_contact_keyboard(lang_code, user['phone'])
        text = await get_lang_text('phone_ask_text', lang_code)
        await query.message.delete()
        await query.message.answer(text, reply_markup=keyboard_markup)
        await MenuData.CONTACT_MENU.set()
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await query.message.answer(text)



@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=MenuData.CONTACT_MENU)
@dp.message_handler(content_types=types.ContentTypes.CONTACT, state='*')
async def contact_type_handler(msg: types.Message, state: FSMContext):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):

        carts = await db.get_cart_all(msg.from_user.id)
        if carts: 
            user = await db.get_user(msg.from_user.id)
            keyboard_markup = await universal_keyboard('delivery_or_get', lang_code)
            text = await get_lang_text('delivery_or_get_text', lang_code)
            await state.update_data(
                {'phone': f"{msg.contact.phone_number}"}
            )
            await msg.answer(text, reply_markup=keyboard_markup)
            await MenuData.DELIVERY_TYPE.set()
        else:
            keyboard_markup = await main_menu_keyboard(lang_code)
            await msg.answer(text = await get_lang_text('empty_cart_text', lang_code), keyboard_markup=keyboard_markup)
            await MenuData.MENU.set() 
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.message.answer(text)


@dp.message_handler(state=MenuData.CONTACT_MENU)
async def contact_text_handler(msg: types.Message, state: FSMContext):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        carts = await db.get_cart_all(msg.from_user.id)
        if carts: 
            phone = ''.join(msg.text.strip().split())
            if bool(re.match(PHONE_EXP, phone)):
                keyboard_markup = await universal_keyboard('delivery_or_get', lang_code)
                text = await get_lang_text('delivery_or_get_text', lang_code)
                await state.update_data(
                    {'phone': msg.text}
                )
                await MenuData.DELIVERY_TYPE.set()
            else:
                user = await db.get_user(msg.from_user.id)
                keyboard_markup = await ask_contact_keyboard(lang_code, user['phone'])
                text = await get_lang_text('phone_ask_text', lang_code)
            await msg.answer(text, reply_markup=keyboard_markup)
        else:
            keyboard_markup = await main_menu_keyboard(lang_code)
            await msg.answer(text = await get_lang_text('empty_cart_text', lang_code), keyboard_markup=keyboard_markup)
            await MenuData.MENU.set()
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.answer(text)


@dp.message_handler(lambda message: message.text in elements_to_list('delivery_or_get'), state=MenuData.DELIVERY_TYPE)
@dp.message_handler(lambda message: message.text in elements_to_list('delivery_or_get'), state='*')
async def delivery_or_get_text_handler(msg: types.Message, state: FSMContext):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        carts = await db.get_cart_all(msg.from_user.id)
        if carts:
            if msg.text == "Yetkazib berish" or msg.text == "Доставка":
                user = await db.get_user(msg.from_user.id)
                keyboard_markup = await ask_location_keyboard(lang_code, user['address'])
                text = await get_lang_text('location_ask_text', lang_code)
                await MenuData.LOCATION_MENU.set()
            elif msg.text == "Olib ketish" or msg.text == "Самовывоз":
                fillials = await db.get_fillials()
                keyboard_markup = await fillial_keyboard(fillials, lang_code)
                text = await get_lang_text('order_get_fillial', lang_code)
                await MenuData.FILLIAL.set()
            else:
                keyboard_markup = await universal_keyboard('delivery_or_get', lang_code)
                text = await get_lang_text('delivery_or_get_text', lang_code)

            await msg.answer(text, reply_markup=keyboard_markup)
        else:
            keyboard_markup = await main_menu_keyboard(lang_code)
            await msg.answer(text = await get_lang_text('empty_cart_text', lang_code), keyboard_markup=keyboard_markup)
            await MenuData.MENU.set()
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.answer(text)


@dp.message_handler(state=MenuData.FILLIAL)
async def fillial_choose_handler(msg: types.Message, state: FSMContext):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        carts = await db.get_cart_all(msg.from_user.id)
        if carts:
            fillial = await db.get_fillial_by_name(msg.text)
            if fillial:
                await state.update_data(
                    {
                        'is_pick_up': True,
                        'address': fillial['address'],
                        'latitude': fillial['latitude'],
                        'longitude': fillial['longitude'],
                    }
                )
                keyboard_markup = await payment_keyboard(lang_code)
                text = await get_lang_text('payment_ask_text', lang_code)
                await msg.answer(text, reply_markup=keyboard_markup)
                await MenuData.PAYMENT_MENU.set()
            else:
                fillials = await db.get_fillials()
                keyboard_markup = await fillial_keyboard(fillials, lang_code)
                text = await get_lang_text('order_get_fillial', lang_code)
                await msg.answer(text, reply_markup=keyboard_markup)
        else:
            keyboard_markup = await main_menu_keyboard(lang_code)
            await msg.answer(text = await get_lang_text('empty_cart_text', lang_code), keyboard_markup=keyboard_markup)
            await MenuData.MENU.set()
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.answer(text)
        

@dp.message_handler(content_types=types.ContentTypes.LOCATION, state=MenuData.LOCATION_MENU)
@dp.message_handler(content_types=types.ContentTypes.LOCATION, state='*')
async def location_type_handler(msg: types.Message, state: FSMContext):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        carts = await db.get_cart_all(msg.from_user.id)
        if carts:
            await state.update_data(
                {
                    'latitude': msg.location.latitude,
                    'longitude': msg.location.longitude,
                }
            )
            geolocator = Nominatim(user_agent="my_geocoder")
            geolocator.headers['Accept-Language'] = lang_code
            location = geolocator.reverse((msg.location.latitude, msg.location.longitude), exactly_one=True)
            keyboard_markup = await confirm_location_keyboard(lang_code)
            text = await get_lang_text('location_confirm_text', lang_code)
            text += "\n" + str(location.address)
            await msg.answer(text, reply_markup=keyboard_markup)
            await MenuData.LOCATION_CONFIRM_MENU.set()
        else:
            keyboard_markup = await main_menu_keyboard(lang_code)
            await msg.answer(text = await get_lang_text('empty_cart_text', lang_code), keyboard_markup=keyboard_markup)
            await MenuData.MENU.set()
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.answer(text)
        
      
@dp.message_handler(state=MenuData.LOCATION_MENU)
async def location_type_address_handler(msg: types.Message, state: FSMContext):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        carts = await db.get_cart_all(msg.from_user.id)
        if carts:
            user = await db.get_user(msg.from_user.id)
            if msg.text == user['address']:
                await state.update_data(
                    {   
                        'latitude': user['latitude'],
                        'longitude': user['longitude'],
                    }
                )
                keyboard_markup = await confirm_location_keyboard(lang_code)
                text = await get_lang_text('location_confirm_text', lang_code)
                text += "\n" + str(user['address'])
                await msg.answer(text, reply_markup=keyboard_markup)
                await MenuData.LOCATION_CONFIRM_MENU.set()
            else:
                keyboard_markup = await ask_location_keyboard(lang_code, user['address'])
                text = await get_lang_text('location_ask_text', lang_code)
                await msg.answer(text, reply_markup=keyboard_markup)
                await MenuData.LOCATION_MENU.set()
        else:
            keyboard_markup = await main_menu_keyboard(lang_code)
            await msg.answer(text = await get_lang_text('empty_cart_text', lang_code), keyboard_markup=keyboard_markup)
            await MenuData.MENU.set()
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.answer(text)
    

@dp.message_handler(lambda message: message.text in two_keys_to_list('location_confirm_yes', 'location_confirm_no'), state=MenuData.LOCATION_CONFIRM_MENU)
@dp.message_handler(lambda message: message.text in two_keys_to_list('location_confirm_yes', 'location_confirm_no'), state='*')
async def location_confirm_handler(msg: types.Message, state: FSMContext):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')

    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        carts = await db.get_cart_all(msg.from_user.id)
        if carts:
            latitude = lang_data.get('latitude')
            longitude = lang_data.get('longitude')
            keyboard_markup = None
            
            if msg.text == await get_lang_text('location_confirm_yes', lang_code):
                geolocator = Nominatim(user_agent="my_geocoder")
                geolocator.headers['Accept-Language'] = 'ru-RU'
                location = geolocator.reverse((latitude, longitude), exactly_one=True)

                if location and "Ташкент" == location.raw.get('address', {}).get('city'):
                    user = await db.get_user(msg.from_user.id)
                    await state.update_data({'address': location.address})   
                    
                    keyboard_markup = await payment_keyboard(lang_code)
                    text = await get_lang_text('payment_ask_text', lang_code)
                    await MenuData.PAYMENT_MENU.set()
                else:
                    keyboard_markup = await main_menu_keyboard(lang_code)
                    text = await get_lang_text('location_out_text', lang_code)
                    await MenuData.MENU.set()
            else:
                await state.update_data({'latitude': None, 'longitude': None})  
                user = await db.get_user(msg.from_user.id) 
                keyboard_markup = await ask_location_keyboard(lang_code, user['address'])
                text = await get_lang_text('location_ask_text', lang_code)
                await MenuData.LOCATION_MENU.set()

            if keyboard_markup is None:
                await msg.answer(text, reply_markup=types.ReplyKeyboardRemove())
            else:
                await msg.answer(text, reply_markup=keyboard_markup)
        else:
            keyboard_markup = await main_menu_keyboard(lang_code)
            await msg.answer(text = await get_lang_text('empty_cart_text', lang_code), keyboard_markup=keyboard_markup)
            await MenuData.MENU.set()
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.answer(text)


@dp.message_handler(lambda message: message.text in payment_list(), state=MenuData.PAYMENT_MENU)
@dp.message_handler(lambda message: message.text in payment_list(), state='*')
async def payment_type_handler(msg: types.Message, state: FSMContext):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        carts = await db.get_cart_all(msg.from_user.id)
        if carts:
            sended_text = await get_lang_text('order_sended', lang_code)
            main_menu_keyb = await main_menu_keyboard(lang_code)
            await msg.answer(sended_text, reply_markup=main_menu_keyb)
            await MenuData.MENU.set()
            
            if msg.text in ["Click",]:
                payment_click = True
            else:
                payment_click = False
                
            datas = await checkout_data(msg.from_user.id, lang_data, payment_click, lang_code)
            if datas:
                await state.update_data(
                    {'is_pick_up': False}
                )
                await db.drop_all_cart_item(msg.from_user.id)
                keyboard_markup = await main_menu_keyboard(lang_code)
                await msg.answer(text=datas['text'], reply_markup=keyboard_markup)
                await MenuData.MENU.set()
                # admin send
                order_data = datas['order']
                geolocator = Nominatim(user_agent="my_geocoder")
                if order_data['is_pick_up']:
                    text_for_admin = f"Новый заказ: №{order_data['id']}\n\nАдрес получения заказа: {order_data['address']}\n\nТел: {order_data['phone_number']}\n\n"
                else:
                    text_for_admin = f"Новый заказ: №{order_data['id']}\n\nАдрес: {order_data['address']}\n\nТел: {order_data['phone_number']}\n\n"
                text_for_admin += datas['text2']
                payment_text = "To'lov turi: Click" if order_data['payment_click'] else "To'lov turi: Naqt"
                text_for_admin +="\n" + f"Umumiy: {order_data['amount']}\n\n" + payment_text
                
                for admin in ADMINS:
                    try:
                        if payment_click:
                            keyboard = await admin_checkout_payment_keyboard(order_data['id'], msg.from_user.id, lang_code)
                        else:
                            keyboard = await admin_checkout_keyboard(order_data['id'], msg.from_user.id, lang_code)
                        await dp.bot.send_location(admin, latitude=order_data['latitude'], longitude=order_data['longitude'])
                        await dp.bot.send_message(admin, text_for_admin, reply_markup=keyboard)
                    except Exception as err:
                        logging.exception(err)
                if order_data['payment_click']:
                    pay_link = await send_click_data_to_backend(order_data['id'], order_data['amount'], phone=order_data['phone_number'])
                    if pay_link:
                        await msg.answer(f"{pay_link}")
                    else:
                        await msg.answer("Error sending data to the payment link generator.")
                for super1 in SUPERUSERS:
                    try:
                        await dp.bot.send_location(super1, latitude=order_data['latitude'], longitude=order_data['longitude'])
                        await dp.bot.send_message(super1, text_for_admin)
                    except Exception as err:
                        logging.exception(err)
            else:
                keyboard_markup = await main_menu_keyboard(lang_code)
                await msg.answer(text="Произошла ошибка", reply_markup=keyboard_markup)        
                await MenuData.MENU.set()  
        else:
            keyboard_markup = await main_menu_keyboard(lang_code)
            await msg.answer(text = await get_lang_text('empty_cart_text', lang_code), keyboard_markup=keyboard_markup)
            await MenuData.MENU.set()
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await msg.answer(text)


async def checkout_data(user_id, state, payment_click, lang_code):
    current_time = get_tashkent_time()
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    carts = await db.get_cart_all(user_id)
    phone = state.get('phone')
    address = state.get('address')
    latitude = state.get('latitude')
    longitude = state.get('longitude')
    is_pick_up = state.get('is_pick_up', False)
    amount = state.get('amount')
    delivery_amount = 0
    if not is_pick_up:
        if int(amount) < 300000:
            delivery_amount = 35000
            amount = int(amount) + 35000
    status = 'active'
    is_paid = False
    
    text2 = ""
    try:
        order = await db.create_order(user_id, phone, lang_code, address, latitude, longitude, amount, status, payment_click, is_paid, current_time, delivery_amount, is_pick_up)
        if is_pick_up:  
            text = get_lang_sinc_args_text('order_number_get_text', lang_code, order['id'], get_lang_sinc_text(order['status'], lang_code), order['address'])
        else:
            text = get_lang_sinc_args_text('order_number_text', lang_code, order['id'], get_lang_sinc_text(order['status'], lang_code), order['address'])
        products_price = 0
        for cart in carts:
            product = await db.get_product_by_id(cart['item_id'])
            prod_title = f"title_{lang_code}"
            text2 += f"{product[prod_title]} {product['price']}/{product['org_measure']} x {cart['item_count']}/{product['measure']}\n"
        
            item = await db.create_order_item(order['id'], product['id'], cart['item_count'], product['price'], product['min_count'], product['measure'], product['org_count_in_measure'], product['org_measure'])
            products_price += cart['item_count'] * product['price'] / product['org_count_in_measure']
    except Exception as e:
        print(f"Error creating order: {e}")
        return
    text += "\n" + text2
    delivery_fee = 0
    if not is_pick_up:
        if products_price < 300000:
            delivery_fee = 35000
            
    delivery_fee_text = get_lang_sinc_text("delivery_fee_free", lang_code) if delivery_fee == 0 else str(35000) + get_lang_sinc_text("sum", lang_code)
    payment_text = "Click" if order['payment_click'] else get_lang_sinc_text("order_payment_type_cash_text", lang_code)
    if is_pick_up:
        text += get_lang_sinc_args_text("order_payment_get_text", lang_code, payment_text, products_price, amount)
    else:
        text += get_lang_sinc_args_text("order_payment_text", lang_code, payment_text, products_price, delivery_fee_text, amount)

    delivery_text = get_lang_sinc_args_text("order_payment_waiting_with_time_text", lang_code) if order['payment_click'] else get_lang_sinc_args_text("order_payment_notwaiting_with_time_text", lang_code)
    text += delivery_text
    
    
    if is_pick_up:
        phone_update = await db.update_user_phone(phone, user_id)
    else:
        address_update = await db.update_user_address(address, latitude, longitude, phone, user_id)

    return {
        "text": text,
        "text2": text2,
        "order": order,
        "products_price": products_price
    }


async def send_click_data_to_backend(order_id, amount, phone=False):
    current_time = get_tashkent_time()
    transaction = await db.create_click_transaction(order_id, amount, current_time)
    order = await db.update_order_transaction(transaction['id'], order_id)
    
    url = f"http://{IP}/click/service/create_invoice/"
    data = {
        "transaction_id": transaction['id'],
        "phone_number": phone,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                return "Chek kiritilgan raqamga yuborildi"
            else:
                return "Xatolik mavjud"