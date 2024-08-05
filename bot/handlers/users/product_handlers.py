import os
import asyncio
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from loader import dp, db

from tashkent_time import get_tashkent_time

from handlers.users.lang import get_lang_text
from keyboards.inline.product_inline_keyboards import (
    korzina_cd,
    count_item,
    add_item,
    subtraction_item,
    item_keyboard,
)
from keyboards.inline.category_inline import (
    product_item,
    products_inline_keyboard,
)


image_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'site', 'media'))



@dp.callback_query_handler(product_item.filter(), state='*')
async def product_detail_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    """This function is for product details"""
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
    
        prod_id = callback_data['prod_id']
        item = await db.get_product(int(prod_id))
        if not item:
            return
        if item[f'about_{lang_code}'] is None:
            desc = ''
        else:
            desc = item[f'about_{lang_code}']
        markup_inline = await item_keyboard(item_id=item['id'], current_count=item['min_count'], min_count=item['min_count'], measure=item['measure'], lang_code=lang_code, parent_id=item['category_id'], child_type='prod')
        photo_path = os.path.join(image_directory, item['photo'])
        with open(photo_path, 'rb') as photo:
            if query.message.photo:
                await query.message.edit_media(media=types.InputMediaPhoto(photo), reply_markup=markup_inline)
                await query.message.edit_caption(caption=f"Narxi: {item['price']}\n{desc}", reply_markup=markup_inline)
            else:
                await query.message.delete()
                await query.message.answer_photo(photo=photo, caption=f"Narxi: {item['price']}\n{desc}", reply_markup=markup_inline)
            await query.answer(cache_time=0)
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await query.message.answer(text)


@dp.callback_query_handler(subtraction_item.filter(), state='*')
async def subtract_item_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
    
        item_id = callback_data['item_id']     
        current_count = int(callback_data['current_count'])
        min_count = int(callback_data['min_count']) 
        measure = callback_data['measure'] 
        parent_id = callback_data['parent_id']    
        child_type = callback_data['child_type']   
        
        if current_count <= min_count:
            await query.answer(cache_time=1)
            return
        new_markup = await item_keyboard(item_id, current_count - min_count, min_count, measure, lang_code, parent_id, child_type)
        
        await query.message.edit_reply_markup(reply_markup=new_markup)
        await query.answer(cache_time=0)
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await query.message.answer(text)


@dp.callback_query_handler(add_item.filter(), state='*')
async def add_item_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        item_id = callback_data['item_id']
        current_count = int(callback_data['current_count'])
        min_count = int(callback_data['min_count'])
        measure = callback_data['measure']    
        parent_id = callback_data['parent_id']    
        child_type = callback_data['child_type']   
        
        new_markup = await item_keyboard(item_id, current_count + min_count, min_count, measure, lang_code, parent_id, child_type)
        await query.message.edit_reply_markup(reply_markup=new_markup)
        await query.answer(cache_time=0)
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await query.message.answer(text)


@dp.callback_query_handler(count_item.filter(), state='*')
async def count_item_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    await asyncio.sleep(0.2)
    current_count = int(callback_data['current_count'])
    await query.answer(f"{current_count}")


@dp.callback_query_handler(korzina_cd.filter(), state='*')
async def add_to_cart_handler(query: CallbackQuery, callback_data: dict, state: FSMContext = None):
    lang_data = await state.get_data()
    lang_code = lang_data.get('lang', 'uz')
    current_time = get_tashkent_time()
    if (8 <= current_time.hour < 23) or (current_time.hour == 23 and current_time.minute <= 15):
        item_id = int(callback_data['item_id'])
        current_count = int(callback_data['current_count'])
        parent_id = callback_data['parent_id']    
        
        product = await db.get_cart_item(query.from_user.id, item_id)
        if product:
            prod = await db.update_cart(product['item_count']+current_count, query.from_user.id, item_id)
        else:
            product = await db.add_cart(query.from_user.id, item_id, current_count, current_time)
        
        category = await db.get_category(int(parent_id))
        child_type = "cat" if category['parent_id'] else "main_cat"
        parent_id = category['parent_id'] if category['parent_id'] else "0"
        products = await db.get_products(int(category['id']))
        new_markup = await products_inline_keyboard(products, lang_code, parent_id=parent_id, child_type=child_type)
        
        await query.message.delete()
        await query.message.answer(await get_lang_text('item_added_cart_text', lang_code))
        photo_path = os.path.join(image_directory, category['image'])
        with open(photo_path, 'rb') as photo:
            await query.message.answer_photo(photo=photo, reply_markup=new_markup)
        await query.answer(cache_time=0)
    else:
        text = await get_lang_text('restaurant_closed', lang_code)
        await query.message.answer(text)



