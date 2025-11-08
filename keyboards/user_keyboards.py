from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_scheme_keyboard(button: str, message_id: int, scheme_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=button, callback_data=f'next_scheme_{scheme_id}_{message_id}')],
        ]
    )
    return keyboard