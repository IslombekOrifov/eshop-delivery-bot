import pytz
import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import logging
from tashkent_time import get_tashkent_time

from loader import db

from handlers.users.lang import (
    lang_dict, get_lang_text
)

pre_checkout = CallbackData("precheck", "all")
clear_cart = CallbackData("clearcart", "all")
rm_item = CallbackData("rmitem", "cart_id",)


def make_callback_data(cart_id):
    return rm_item.new(cart_id=cart_id)


async def cart_keyboard(user_id, lang_code):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(
            text=await get_lang_text('cart_clear', lang_code), callback_data=clear_cart.new(all='all')
        ),
        InlineKeyboardButton(
            text=await get_lang_text('cart_clearance', lang_code), callback_data=pre_checkout.new(all='all'), 
        ),
    )
   
    has_cart = False
    current_time = get_tashkent_time()
    carts = await db.get_cart_all(user_id)
    if carts:
        has_cart = True
    text = f"{await get_lang_text('in_cart_text', lang_code)}:\n"
    products_price = 0
    for cart in carts:
        product = await db.get_product_by_id(cart['item_id'])
        prod_title = f"title_{lang_code}"
        text += f"{product[prod_title]} {product['price']}/{product['org_measure']} x {cart['item_count']}/{product['measure']}\n"
        products_price += cart['item_count'] * product['price'] / product['org_count_in_measure']
        markup.row(
            InlineKeyboardButton(
                text=f"❌ {product[prod_title]}",
                callback_data=make_callback_data(
                    cart_id=cart['id']
                ),
            )
        )
    return {
        "keyboard": markup,
        "has_cart": has_cart,
        "text": text,
        "products_price": products_price
    }