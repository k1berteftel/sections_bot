from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, ShowMode

from keyboards.user_keyboards import get_scheme_keyboard
from database.action_data_class import DataInteraction
from states.state_groups import startSG


user_router = Router()


@user_router.message(CommandStart())
async def start_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, command: CommandObject):
    args = command.args
    scheme_id = None
    #referral = None
    if args:
        link_ids = await session.get_links()
        ids = [i.link for i in link_ids]
        if args in ids:
            await session.add_admin(msg.from_user.id, msg.from_user.full_name)
            await session.del_link(args)
        elif not await session.check_user(msg.from_user.id):
            deeplinks = await session.get_deeplinks()
            deep_list = [i.link for i in deeplinks]
            if args in deep_list:
                await session.add_entry(args)
        elif args in [scheme.deeplink for scheme in await session.get_schemes()]:
            schemes = await session.get_schemes()
            for scheme in schemes:
                if scheme.deeplink == args:
                    scheme_id = scheme.id
                    break
            #try:
                #args = int(args)
                #users = [user.user_id for user in await session.get_users()]
                #if args in users:
                    #referral = args
                    #await session.add_refs(args)
            #except Exception as err:
                #print(err)
    await session.add_user(msg.from_user.id, msg.from_user.username if msg.from_user.username else 'Отсутствует',
                           msg.from_user.full_name)
    if scheme_id:
        messages = await session.get_scheme_messages(scheme_id)
        message = messages[0]
        keyboard = await get_scheme_keyboard(message.button, 0, scheme_id)
        await msg.bot.copy_message(
            chat_id=msg.chat.id,
            message_id=message.message_id,
            from_chat_id=message.chat_id,
            reply_markup=keyboard
        )
        return
    if dialog_manager.has_context():
        await dialog_manager.done()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
        counter = 1
        while dialog_manager.has_context():
            await dialog_manager.done()
            try:
                await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id + counter)
            except Exception:
                ...
            counter += 1
    await dialog_manager.start(state=startSG.start, mode=StartMode.RESET_STACK)


@user_router.callback_query(F.data.startswith("next_scheme"))
async def scheme_pager(clb: CallbackQuery, session: DataInteraction, dialog_manager: DialogManager):
    print('here')
    data = clb.data.split('_')
    message_id = int(data[-1])
    scheme_id = int(data[-2])
    messages = await session.get_scheme_messages(scheme_id)
    if len(messages) == message_id + 1:
        await clb.answer('Возвращаюсь в главное меню')
        await dialog_manager.start(startSG.schemes, mode=StartMode.RESET_STACK)
        return
    message = messages[message_id+1]
    keyboard = await get_scheme_keyboard(message.button, message_id+1, scheme_id)
    await clb.bot.copy_message(
        chat_id=clb.message.chat.id,
        message_id=message.message_id,
        from_chat_id=message.chat_id,
        reply_markup=keyboard
    )
