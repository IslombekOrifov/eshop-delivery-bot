from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from handlers.users.lang import lang_dict, get_lang_text


async def ask_contact_keyboard(lang_code, phone=None):
    menu_keyb = ReplyKeyboardMarkup(resize_keyboard=True)
    if phone:
        menu_keyb.keyboard.append([KeyboardButton(text=phone)])
        
    menu_keyb.keyboard.extend([
        [
            KeyboardButton(text = await get_lang_text('phone_text', lang_code), request_contact=True),
        ],
        [
            KeyboardButton(text = await get_lang_text('back', lang_code)),
        ],
    ])
    return menu_keyb


async def ask_location_keyboard(lang_code, address=None):
    menu_keyb = ReplyKeyboardMarkup(resize_keyboard=True)
    
    if address:
        menu_keyb.keyboard.append([KeyboardButton(text=address)])
    
    menu_keyb.keyboard.extend([
        [
            KeyboardButton(text=await get_lang_text('location_text', lang_code), request_location=True),
        ],
        [
            KeyboardButton(text=await get_lang_text('back', lang_code)),
        ],
    ])
    
    return menu_keyb


async def confirm_location_keyboard(lang_code):
    menu_keyb = ReplyKeyboardMarkup(
        keyboard = [
            [
                KeyboardButton(text = await get_lang_text('location_confirm_yes', lang_code)),
                KeyboardButton(text = await get_lang_text('location_confirm_no', lang_code)),
            ],
            [
                KeyboardButton(text = await get_lang_text('back', lang_code)),
            ],
        ],
        resize_keyboard=True,
    )
    return menu_keyb


async def payment_keyboard(lang_code):
    menu_keyb = ReplyKeyboardMarkup(
        keyboard = [
            [
                KeyboardButton(text = await get_lang_text('payment_text', lang_code)),
            ],
            [
                KeyboardButton(text='Click'),
            ],
            [
                KeyboardButton(text = await get_lang_text('back', lang_code)),
            ],
        ],
        resize_keyboard=True,
    )
    return menu_keyb


async def universal_keyboard(text, lang_code):
    keyb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyb_text = lang_dict.get(text).get(lang_code)
    button = (KeyboardButton(text=f"{menu}") for menu in keyb_text)
    keyb.add(*button)
    keyb.add(KeyboardButton(text=await get_lang_text('back', lang_code)))
    return keyb


async def fillial_keyboard(datas, lang_code):
    keyb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button = (KeyboardButton(text=f"{info['name']}") for info in datas)
    keyb.add(*button)
    keyb.add(KeyboardButton(text=await get_lang_text('back', lang_code)))
    return keyb