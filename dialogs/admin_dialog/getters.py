import os
import datetime

from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.tables import get_table
from utils.database_utils import get_invite_bot_users
from keyboards.admin_keyboards import get_watch_scheme_keyboard
from utils.build_ids import get_random_id
from utils.schedulers import send_messages
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import startSG, adminSG


async def get_static(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    users = await session.get_users()
    active = 0
    entry = {
        'today': 0,
        'yesterday': 0,
        '2_day_ago': 0
    }
    activity = 0
    for user in users:
        if user.active:
            active += 1
        for day in range(0, 3):
            #print(user.entry.date(), (datetime.datetime.today() - datetime.timedelta(days=day)).date())
            if user.entry.date() == (datetime.datetime.today() - datetime.timedelta(days=day)).date():
                if day == 0:
                    entry['today'] = entry.get('today') + 1
                elif day == 1:
                    entry['yesterday'] = entry.get('yesterday') + 1
                else:
                    entry['2_day_ago'] = entry.get('2_day_ago') + 1
        if user.activity.timestamp() > (datetime.datetime.today() - datetime.timedelta(days=1)).timestamp():
            activity += 1

    text = (f'<b>Статистика на {datetime.datetime.today().strftime("%d-%m-%Y")}</b>\n\nВсего пользователей: {len(users)}'
            f'\n - Активные пользователи(не заблокировали бота): {active}\n - Пользователей заблокировали '
            f'бота: {len(users) - active}\n - Провзаимодействовали с ботом за последние 24 часа: {activity}\n\n'
            f'<b>Прирост аудитории:</b>\n - За сегодня: +{entry.get("today")}\n - Вчера: +{entry.get("yesterday")}'
            f'\n - Позавчера: + {entry.get("2_day_ago")}')
    await clb.message.answer(text=text)


async def get_users_txt(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    users = await session.get_users()
    columns = []
    for user in users:
        columns.append(
            [
                user.name,
                '@' + user.username if user.username else '-',
                user.entry.strftime("%d-%m-%Y"),
                user.activity.strftime("%d-%m-%Y")
            ]
        )
    columns.insert(0, ['Никнейм', 'Юзернейм', 'Впервые запустил бота', 'Дата последней активности'])
    table = get_table(columns, 'Пользователи')
    await clb.message.answer_document(document=FSInputFile(path=table))
    try:
        os.remove(table)
    except Exception:
        ...


async def schemes_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    schemes = await session.get_schemes()
    text = ''
    if schemes:
        counter = 1
        for scheme in schemes:
            text += (f'({counter}) - <em>{scheme.name}</em> ({len(scheme.messages)}💬)\n\tСсылка: '
                     f'<code>https://t.me/kurtrobot?start={scheme.deeplink}</code>\n')
    else:
        text = 'У вас пока не добавлено схем'

    return {'text': text}


async def get_scheme_name(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['name'] = text
    await dialog_manager.switch_to(adminSG.get_scheme_message)


async def get_scheme_message_getter(dialog_manager: DialogManager, **kwargs):
    messages = dialog_manager.dialog_data.get('messages')
    name = dialog_manager.dialog_data.get('name')
    return {
        'number': len(messages) + 1 if messages else 1,
        'name': name
    }


async def get_scheme_message(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    if msg.text and len(msg.text) >= 4096:
        await msg.answer('Максимальное количество символов в сообщении не более 4096, пожалуйста сократите сообщение')
        return
    if msg.caption and len(msg.caption) >= 1024:
        await msg.answer('Максимальное количество символов в тексте под медиа не более 1024, пожалуйста сократите сообщение')
        return
    dialog_manager.dialog_data['msg_id'] = msg.message_id
    dialog_manager.dialog_data['chat_id'] = msg.chat.id
    await dialog_manager.switch_to(adminSG.get_message_button)


async def get_message_button(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['button'] = text
    await dialog_manager.switch_to(adminSG.confirm_scheme)


async def confirm_scheme_getter(dialog_manager: DialogManager, **kwargs):
    messages = dialog_manager.dialog_data.get('messages')
    name = dialog_manager.dialog_data.get('name')
    return {
        'number': len(messages) + 1 if messages else 1,
        'name': name
    }


async def add_message_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    message_id = dialog_manager.dialog_data.get('msg_id')
    chat_id = dialog_manager.dialog_data.get('chat_id')
    scheme_name = dialog_manager.dialog_data.get('name')
    button = dialog_manager.dialog_data.get('button')
    messages = dialog_manager.dialog_data.get('messages', [])
    messages.append(
        {
            'message_id': message_id,
            'chat_id': chat_id,
            'button': button
        }
    )
    dialog_manager.dialog_data['messages'] = messages
    await dialog_manager.switch_to(adminSG.get_scheme_message)


async def save_scheme(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    message_id = dialog_manager.dialog_data.get('msg_id')
    chat_id = dialog_manager.dialog_data.get('chat_id')
    scheme_name = dialog_manager.dialog_data.get('name')
    button = dialog_manager.dialog_data.get('button')
    messages = dialog_manager.dialog_data.get('messages', [])
    messages.append(
        {
            'message_id': message_id,
            'chat_id': chat_id,
            'button': button
        }
    )
    dialog_manager.dialog_data['messages'] = messages
    await session.add_scheme(scheme_name, get_random_id(), messages)
    await clb.answer('Новый раздел был успешно добавлен')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.schemes)


async def choose_scheme_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    buttons = [(scheme.name, scheme.id) for scheme in await session.get_schemes()]
    return {
        'items': buttons
    }


async def scheme_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['scheme_id'] = int(item_id)
    await dialog_manager.switch_to(adminSG.scheme_menu)


async def scheme_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    scheme_id = dialog_manager.dialog_data.get('scheme_id')
    scheme = await session.get_scheme(scheme_id)
    return {
        'name': scheme.name,
        'messages': len(scheme.messages),
        'deeplink': f'https://t.me/kurtrobot?start={scheme.deeplink}'
    }


async def scheme_message_choose_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    scheme_id = dialog_manager.dialog_data.get('scheme_id')
    messages = await session.get_scheme_messages(scheme_id)
    counter = 0
    buttons = []
    for message in messages:
        buttons.append((f'Сообщение {counter+1}', counter))
        counter += 1
    return {
        'items': buttons
    }


async def watch_message_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    scheme_id = dialog_manager.dialog_data.get('scheme_id')
    state: FSMContext = dialog_manager.middleware_data.get('state')
    await state.update_data(scheme_id=scheme_id)
    messages = await session.get_scheme_messages(scheme_id)
    message = messages[int(item_id)]
    keyboard = await get_watch_scheme_keyboard(message.button, message.id)
    await clb.bot.copy_message(
        chat_id=clb.message.chat.id,
        message_id=message.message_id,
        from_chat_id=message.chat_id,
        reply_markup=keyboard
    )


async def watch_scheme_message(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    scheme_id = dialog_manager.dialog_data.get('scheme_id')
    scheme = await session.get_scheme(scheme_id)
    state: FSMContext = dialog_manager.middleware_data.get('state')
    await state.update_data(scheme_id=scheme_id, message_id=0)
    messages = await session.get_scheme_messages(scheme_id)
    message = messages[0]
    keyboard = await get_watch_scheme_keyboard(message.button, message.id)
    await clb.bot.copy_message(
        chat_id=clb.message.chat.id,
        message_id=message.message_id,
        from_chat_id=message.chat_id,
        reply_markup=keyboard
    )


async def change_scheme_name(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    scheme_id = dialog_manager.dialog_data.get('scheme_id')
    await session.set_scheme_name(scheme_id, text)
    await msg.answer('Название схемы было успешно изменено')
    try:
        await msg.delete()
    except Exception:
        ...
    await dialog_manager.switch_to(adminSG.scheme_menu)


async def change_scheme_message(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    message_id = dialog_manager.dialog_data.get('message_id')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_message(message_id, message_id=msg.message_id, chat_id=msg.chat.id)
    await dialog_manager.switch_to(adminSG.change_scheme_button)


async def change_scheme_button(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    message_id = dialog_manager.dialog_data.get('message_id')
    await session.update_message(message_id, button=text)


async def del_scheme(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    scheme_id = dialog_manager.dialog_data.get('scheme_id')
    await session.del_scheme(scheme_id)
    dialog_manager.dialog_data.clear()
    await clb.answer('Схема была успешно удаленна')
    await dialog_manager.switch_to(adminSG.schemes)


async def deeplink_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    links = await session.get_deeplinks()
    text = ''
    for link in links:
        text += f'https://t.me/kurtrobot?start={link.link}: {link.entry}\n'  # Получить ссылку на бота и поменять
    return {'links': text}


async def add_deeplink(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.add_deeplink(get_random_id())
    await dialog_manager.switch_to(adminSG.deeplink_menu)


async def del_deeplink(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_deeplink(item_id)
    await clb.answer('Ссылка была успешно удаленна')
    await dialog_manager.switch_to(adminSG.deeplink_menu)


async def del_deeplink_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    links = await session.get_deeplinks()
    buttons = []
    for link in links:
        buttons.append((f'{link.link}: {link.entry}', link.link))
    return {'items': buttons}


async def del_admin(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_admin(int(item_id))
    await clb.answer('Админ был успешно удален')
    await dialog_manager.switch_to(adminSG.admin_menu)


async def admin_del_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    admins = await session.get_admins()
    buttons = []
    for admin in admins:
        buttons.append((admin.name, admin.user_id))
    return {'items': buttons}


async def refresh_url(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    id: str = dialog_manager.dialog_data.get('link_id')
    dialog_manager.dialog_data.clear()
    await session.del_link(id)
    await dialog_manager.switch_to(adminSG.admin_add)


async def admin_add_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    id = get_random_id()
    dialog_manager.dialog_data['link_id'] = id
    await session.add_link(id)
    return {'id': id}


async def admin_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    admins = await session.get_admins()
    text = ''
    for admin in admins:
        text += f'{admin.name}\n'
    return {'admins': text}


async def mail_choose(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['audience'] = clb.data.split('_')[0]
    await dialog_manager.switch_to(adminSG.get_mail)


async def get_mail(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    if msg.text:
        dialog_manager.dialog_data['text'] = msg.text
    elif msg.photo:
        dialog_manager.dialog_data['photo'] = msg.photo[0].file_id
        dialog_manager.dialog_data['caption'] = msg.caption
    elif msg.video:
        dialog_manager.dialog_data['video'] = msg.video.file_id
        dialog_manager.dialog_data['caption'] = msg.caption
    else:
        await msg.answer('Что-то пошло не так, пожалуйста попробуйте снова')
    await dialog_manager.switch_to(adminSG.get_time)


async def get_time(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        time = datetime.datetime.strptime(text, '%H:%M %d.%m')
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['time'] = text
    await dialog_manager.switch_to(adminSG.get_keyboard)


async def get_mail_keyboard(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        buttons = text.split('\n')
        keyboard: list[tuple] = [(i.split('-')[0].strip(), i.split('-')[1].strip()) for i in buttons]
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['keyboard'] = keyboard
    await dialog_manager.switch_to(adminSG.confirm_mail)


async def cancel_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def start_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    time = dialog_manager.dialog_data.get('time')
    keyboard = dialog_manager.dialog_data.get('keyboard')
    audience = dialog_manager.dialog_data.get('audience')
    if audience == 'all':
        users = await session.get_users()
    else:
        bot_users = await get_invite_bot_users()
        if audience == 'subs':
            subs = [bot_user.user_id for bot_user in bot_users if bot_user.subscription]
            users = [user for user in await session.get_users() if user.user_id in subs]
        else:
            not_subs = [bot_user.user_id for bot_user in bot_users if not bot_user.subscription]
            users = [user for user in await session.get_users() if user.user_id in not_subs]
    if keyboard:
        keyboard = [InlineKeyboardButton(text=i[0], url=i[1]) for i in keyboard]
    if not time:
        if dialog_manager.dialog_data.get('text'):
            text: str = dialog_manager.dialog_data.get('text')
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.user_id,
                        text=text.format(name=user.name),
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None
                    )
                    if user.active == 0:
                        await session.set_active(user.user_id, 1)
                except Exception as err:
                    print(err)
                    await session.set_active(user.user_id, 0)
        elif dialog_manager.dialog_data.get('caption'):
            caption: str = dialog_manager.dialog_data.get('caption')
            if dialog_manager.dialog_data.get('photo'):
                for user in users:
                    try:
                        await bot.send_photo(
                            chat_id=user.user_id,
                            photo=dialog_manager.dialog_data.get('photo'),
                            caption=caption.format(name=user.name),
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None
                        )
                        if user.active == 0:
                            await session.set_active(user.user_id, 1)
                    except Exception as err:
                        print(err)
                        await session.set_active(user.user_id, 0)
            else:
                for user in users:
                    try:
                        await bot.send_video(
                            chat_id=user.user_id,
                            video=dialog_manager.dialog_data.get('video'),
                            caption=caption.format(name=user.name),
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None
                        )
                        if user.active == 0:
                            await session.set_active(user.user_id, 1)
                    except Exception as err:
                        print(err)
                        await session.set_active(user.user_id, 0)
    else:
        date = datetime.datetime.strptime(time, '%H:%M %d.%m')
        date = date.replace(year=datetime.datetime.today().year)
        scheduler.add_job(
            func=send_messages,
            args=[bot, session, InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None],
            kwargs={
                'text': dialog_manager.dialog_data.get('text'),
                'caption': dialog_manager.dialog_data.get('caption'),
                'photo': dialog_manager.dialog_data.get('photo'),
                'video': dialog_manager.dialog_data.get('video')
            },
            next_run_time=date
        )
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)

