from aiogram.fsm.state import State, StatesGroup

# Обычная группа состояний


class startSG(StatesGroup):
    start = State()

    schemes = State()

    help = State()


class adminSG(StatesGroup):
    start = State()

    mail_choose = State()
    get_mail = State()
    get_time = State()
    get_keyboard = State()
    confirm_mail = State()

    deeplink_menu = State()
    deeplink_del = State()

    admin_menu = State()
    admin_del = State()
    admin_add = State()

    schemes = State()

    get_scheme_name = State()
    get_scheme_message = State()
    get_message_button = State()
    confirm_scheme = State()

    choose_scheme = State()
    scheme_menu = State()
    scheme_message_choose = State()
    change_scheme_name = State()
    change_scheme_message = State()
    change_scheme_button = State()
    del_scheme = State()
