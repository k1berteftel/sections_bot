from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, StartMode, ShowMode

from keyboards.admin_keyboards import get_watch_scheme_keyboard
from database.action_data_class import DataInteraction
from states.state_groups import adminSG


admin_router = Router()


@admin_router.callback_query(F.data == 'next_plug_message')
async def handle_next_message(clb: CallbackQuery, session: DataInteraction, state: FSMContext, dialog_manager: DialogManager):
    pass
    """
    data = await state.get_data()
    scheme_id = data.get('scheme_id')
    message_id = data.get('message_id')
    messages = await session.get_scheme_messages(scheme_id)
    if message_id == len(messages) - 1:
        await clb.answer('Раздел окончен, возвращаюсь в главное меню')
        await dialog_manager.switch_to(adminSG.scheme_menu, show_mode=ShowMode.DELETE_AND_SEND)
        return
    message = messages[message_id+1]
    keyboard = await get_watch_scheme_keyboard(message.button, message.id)
    await clb.bot.copy_message(
        chat_id=clb.message.chat.id,
        message_id=message.message_id,
        from_chat_id=message.chat_id,
        reply_markup=keyboard
    )
    await state.update_data(message_id=message_id+1)
    """


@admin_router.callback_query(F.data.startswith('change_message'))
async def handle_change_message(clb: CallbackQuery, session: DataInteraction, state: FSMContext, dialog_manager: DialogManager):
    dialog_manager.dialog_data['message_id'] = int(clb.data.split('_')[-1])
    await clb.message.delete()
    ctx = dialog_manager.current_context()
    ctx.state = adminSG.change_scheme_message
    await dialog_manager.show(show_mode=ShowMode.DELETE_AND_SEND)


@admin_router.callback_query(F.data.startswith("del_message"))
async def handle_del_message(clb: CallbackQuery, session: DataInteraction, state: FSMContext, dialog_manager: DialogManager):
    message_id = int(clb.data.split('_')[-1])
    await session.del_message(message_id)
    await clb.message.delete()
    await dialog_manager.switch_to(adminSG.scheme_menu, show_mode=ShowMode.DELETE_AND_SEND)
    return


@admin_router.callback_query(F.data == 'close_scheme_watcher')
async def back_main(clb: CallbackQuery, session: DataInteraction, state: FSMContext, dialog_manager: DialogManager):
    print('here')
    print(dialog_manager.current_context().state)
    print(dialog_manager.current_stack())
    await clb.answer()
    await dialog_manager.update({}, show_mode=ShowMode.DELETE_AND_SEND)
