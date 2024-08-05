from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


check_status = CallbackData("order_check", "order_id", "client", "lang_code")
order_confirm = CallbackData("order_confirm", "order_id", "client", "lang_code")
order_reject_all = CallbackData("order_reject_all", "order_id", "message_id", "supplier_id", "client", "lang_code")
order_reject = CallbackData("order_reject", "order_id", "client", "lang_code")
on_way = CallbackData("on_way", "order_id", "admin_msg", "client", "lang_code")
delivered = CallbackData("delivered", "order_id", "client", "lang_code")


async def admin_checkout_keyboard(order_id, client_id, lang_code):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(
            text="Tasdiqlash", callback_data=order_confirm.new(order_id=order_id, client=int(client_id), lang_code=lang_code), 
        ),
        InlineKeyboardButton(
            text="Bekor qilish", callback_data=order_reject.new(order_id=order_id, client=int(client_id), lang_code=lang_code)
        ),
    )
    return markup


async def admin_checkout_payment_keyboard(order_id, client_id, lang_code):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(
            text="Tekshirish", callback_data=check_status.new(order_id=order_id, client=int(client_id), lang_code=lang_code), 
        ),
    )
    return markup


async def admin_order_reject_keyboard(order_id, message_id, supplier_id, client_id, lang_code):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(
            text="Bekor qilish", callback_data=order_reject_all.new(
                order_id=order_id, message_id=message_id, supplier_id=supplier_id,  client=int(client_id), lang_code=lang_code
            )
        ),
    )
    return markup


async def delivered_keyboard(order_id, client_id, lang_code):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(
            text=f"Yetkazib berildi",
            callback_data=delivered.new(
                order_id=order_id, client=client_id, lang_code=lang_code
            ),
        )
    )
    return markup

