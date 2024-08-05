from aiogram.dispatcher.filters.state import StatesGroup, State


class MenuData(StatesGroup):
    LANG_MENU = State()
    MENU = State()
    ADDRESS_MENU = State()
    PRODUCT_MENU = State()
    PRODUCT_DETAIL_MENU = State()
    CONTACT_MENU = State()
    DELIVERY_TYPE = State()
    FILLIAL = State()
    LOCATION_MENU = State()
    LOCATION_CONFIRM_MENU = State()
    FULL_NAME = State()
    DATE_OR_BIRTH = State()
    PAYMENT_MENU = State()
    COMMENT_MENU = State()
    


class AdminData(StatesGroup):
    ADVERTISING = State()