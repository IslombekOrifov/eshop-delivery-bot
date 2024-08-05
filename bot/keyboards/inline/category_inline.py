import pytz
import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import logging

from handlers.users.lang import get_lang_text


category_item = CallbackData("category_item", "cat_id", "title")
product_item = CallbackData("product_item", "prod_id")
fillial_item = CallbackData("fillial_item", "fill_id")
back_menu = CallbackData("back_menu", "child_type", "parent_id")

pre_checkout = CallbackData("precheck", "all")


def make_category_callback_data(cat_id, title):
    return category_item.new(cat_id=cat_id, title=title)

def make_product_callback_data(prod_id):
    return product_item.new(prod_id=prod_id)

def make_fillial_callback_data(fill_id):
    return fillial_item.new(fill_id=fill_id)

def make_back_menu_callback_data(child_type, parent_id):
    return back_menu.new(child_type=child_type, parent_id=parent_id)


async def catagory_inline_keyboard(cat_and_prods, lang_code, parent_id=None, child_type=None, is_main=None):
    markup = InlineKeyboardMarkup(row_width=1)
    
    for cp in cat_and_prods:
        title = cp[f"title_{lang_code}"]
        markup.row(
            InlineKeyboardButton(
                text=f"{title}",
                callback_data=category_item.new(cat_id=cp['id'], title=title),
            )
        )
    if not is_main:
        markup.row(InlineKeyboardButton(
                text=await get_lang_text('back', lang_code), 
                callback_data=make_back_menu_callback_data(parent_id=parent_id, child_type=child_type)
            ),
        )   
    return markup

async def products_inline_keyboard(products, lang_code, parent_id=None, child_type=None, is_main=None):
    markup = InlineKeyboardMarkup(row_width=1)
    
    for product in products:
        title = product[f"title_{lang_code}"]
        markup.row(
            InlineKeyboardButton(
                text=f"{title}",
                callback_data=make_product_callback_data(prod_id=product['id']),
            )
        )
    if not is_main:
        markup.row(InlineKeyboardButton(
                text=await get_lang_text('back', lang_code), 
                callback_data=make_back_menu_callback_data(child_type=child_type, parent_id=parent_id)
            ),
        )   
    return markup


async def fillials_inline_keyboard(fillials, lang_code):
    markup = InlineKeyboardMarkup(row_width=2)
    
    for fillial in fillials:
        title = fillial[f"name"]
        markup.row(
            InlineKeyboardButton(
                text=f"{title}",
                callback_data=make_fillial_callback_data(fill_id=fillial['id']),
            )
        )
    return markup
