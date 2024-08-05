import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from handlers.users.lang import get_lang_text

from keyboards.inline.category_inline import back_menu, make_back_menu_callback_data


korzina_cd = CallbackData("add_korzina", "item_id", "current_count", "parent_id", "child_type")
count_item = CallbackData("count", "item_id", "current_count", "min_count", "measure", "parent_id", "child_type")
add_item = CallbackData("plus", "item_id", "current_count", "min_count", "measure", "parent_id", "child_type")
subtraction_item = CallbackData("minus", "item_id", "current_count", "min_count", "measure", "parent_id", "child_type")


def make_callback_data(item_id, current_count, parent_id, child_type):
    return korzina_cd.new(
        item_id=item_id, current_count=current_count,
        parent_id=parent_id, child_type=child_type
    )

async def item_keyboard(item_id, current_count, min_count, measure, lang_code, parent_id=None, child_type=None):
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup(row_width=3)
    markup.row(
        InlineKeyboardButton(
            text=f"-", callback_data=subtraction_item.new(item_id=item_id, current_count=current_count, min_count=min_count, measure=measure, parent_id=parent_id, child_type=child_type), 
        ),
        InlineKeyboardButton(
            text=f"{current_count} {measure}", callback_data=count_item.new(item_id=item_id, current_count=current_count, min_count=min_count, measure=measure, parent_id=parent_id, child_type=child_type)
        ),
        InlineKeyboardButton(
            text=f"+", callback_data=add_item.new(item_id=item_id, current_count=current_count, min_count=min_count, measure=measure, parent_id=parent_id, child_type=child_type)
        )
    )
    markup.row(
        InlineKeyboardButton(
            text=await get_lang_text('add_to_cart_text', lang_code),
            callback_data=make_callback_data(
                item_id=item_id, current_count=current_count,
                parent_id=parent_id, child_type=child_type
            ),
        )
    )
    markup.row(InlineKeyboardButton(
                text=await get_lang_text('back', lang_code), 
                callback_data=make_back_menu_callback_data(parent_id=parent_id, child_type=child_type)
            ),
        )
    return markup
