import asyncio
import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from loader import dp, db
from states.menuData import MenuData

from handlers.users.lang import (
    get_lang_text, values_to_list
)
from keyboards.default.menu_keyboards import (
    main_menu_keyboard, 
)

from keyboards.inline.cart_inline_keb import (
    cart_keyboard,
)

from keyboards.inline.category_inline import (
    back_menu, catagory_inline_keyboard
)

from keyboards.inline.category_inline import (
    product_item,
    products_inline_keyboard,
)

image_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'site', 'media'))


@dp.message_handler(lambda message: message.text in values_to_list('back'), state=MenuData.COMMENT_MENU)
async def back_main_menu(msg: types.Message, state: FSMContext):
    """ bu funksiya tepadegi ikkita filter uchun ham ishlaydi."""
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    text = await get_lang_text('main_menu_text', lang_code)
    keyboard_markup = await main_menu_keyboard(lang_code)
    await msg.answer(text, reply_markup=keyboard_markup)
    await MenuData.MENU.set()


@dp.message_handler(lambda message: message.text in values_to_list('back'), state=MenuData.CONTACT_MENU)
async def back_from_contact_menu(msg: types.Message, state: FSMContext):
    """ bu funksiya tepadegi ikkita filter uchun ham ishlaydi."""
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    text = await get_lang_text('main_menu_text', lang_code)
    keyboards_markup = await main_menu_keyboard(lang_code)
    cart_data = await cart_keyboard(msg.from_user.id, lang_code)
    
    if cart_data['has_cart']:
        cart_text = cart_data['text']
        products_price = cart_data['products_price']
        cart_keyboard_markup = cart_data['keyboard']
        await state.update_data(
            {'amount': products_price}
        )
        text += f"{await get_lang_text('price_all_text', lang_code)}: {products_price} {await get_lang_text('price_currency_text', lang_code)}"
        await msg.answer(text=cart_text, reply_markup=cart_keyboard_markup)
    await MenuData.MENU.set()
    await msg.answer(text, reply_markup=keyboards_markup)


@dp.message_handler(lambda message: message.text in values_to_list('back'), state=[MenuData.DELIVERY_TYPE, MenuData.FILLIAL, MenuData.LOCATION_MENU, MenuData.LOCATION_CONFIRM_MENU, MenuData.PAYMENT_MENU, MenuData.COMMENT_MENU])
async def back_main_menu(msg: types.Message, state: FSMContext):
    """ bu funksiya tepadegi ikkita filter uchun ham ishlaydi."""
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    text = await get_lang_text('main_menu_text', lang_code)
    keyboard_markup = await main_menu_keyboard(lang_code)
    await msg.answer(text, reply_markup=keyboard_markup)
    await MenuData.MENU.set()


@dp.callback_query_handler(back_menu.filter(), state=MenuData.MENU)
async def back_inline_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    await asyncio.sleep(0.5)
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    
    parent_id = callback_data['parent_id']    
    child_type = callback_data['child_type']
        
    if child_type == "prod":
        category = await db.get_category(int(parent_id))        
        if category['parent_id']:
            child_type = "cat"
        else:
            child_type = "main_cat"
        parent_id = category['parent_id'] if category['parent_id'] else "0"
        products = await db.get_products(int(category['id']))
        new_markup = await products_inline_keyboard(products, lang_code, parent_id=parent_id, child_type=child_type)
        photo_path = os.path.join(image_directory, category['image'])
        with open(photo_path, 'rb') as photo:
            await query.message.edit_media(media=types.InputMediaPhoto(photo), reply_markup=new_markup)
            
    elif child_type == "cat":
        category = await db.get_category(int(parent_id)) 
        if category['parent_id']:
            parent_cat = await db.get_category(category['parent_id']) 
            new_child_type = "main_cat" if parent_cat['parent_id'] else "cat"
        else:
            new_child_type = "main_cat"
            
        sub_category = await db.get_subcategories(int(category['id']))
        new_markup = await catagory_inline_keyboard(sub_category, lang_code, int(category['id']), child_type=new_child_type)
        photo_path = os.path.join(image_directory, category['image'])
        with open(photo_path, 'rb') as photo:
            await query.message.edit_media(media=types.InputMediaPhoto(photo), reply_markup=new_markup)
            
    elif child_type == "main_cat":
        text = await get_lang_text('category_text', lang_code)
        categories = await db.get_categories()
        new_markup = await catagory_inline_keyboard(categories, lang_code, is_main=True)
        photo_path = os.path.join(image_directory, 'logo/logo.jpg')
        with open(photo_path, 'rb') as photo:
            await query.message.edit_media(media=types.InputMediaPhoto(photo), reply_markup=new_markup)
    
    await query.answer(cache_time=0)   