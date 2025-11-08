from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_watch_scheme_keyboard(button: str, message_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=button, callback_data='next_plug_message')],
            [InlineKeyboardButton(text='Редактировать сообщение', callback_data=f'change_message_{message_id}')],
            [InlineKeyboardButton(text='Удалить сообщение', callback_data=f'del_message_{message_id}')],
            [InlineKeyboardButton(text='На главное меню', callback_data='close_scheme_watcher')]
        ]
    )
    return keyboard