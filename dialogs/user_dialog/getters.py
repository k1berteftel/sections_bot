from aiogram.types import CallbackQuery, User, Message, ContentType
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput

from keyboards.user_keyboards import get_scheme_keyboard
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import startSG


config: Config = load_config()


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    admin = False
    admins = [*config.bot.admin_ids]
    admins.extend([admin.user_id for admin in await session.get_admins()])
    if event_from_user.id in admins:
        admin = True
    text = (f'<b>Здарова, {event_from_user.full_name} 👊</b>\n\nЗдесь ты абсолютно БЕСПЛАТНО заработаешь свои первые '
            f'10.000-40.000₽ в интернете.\n\n<b>Меня зовут Курт.</b>\n\n— Я заработал 92к$ за 51 день '
            f'[<a href="https://t.me/c/1861980586/186">ПРУФ</a>]\n— Сделал 5.000.000₽ за 4 дня '
            f'[<a href="https://t.me/c/1861980586/352">ПРУФ</a>]\n— Изменил жизнь сотням людей '
            f'[<a href="https://t.me/locked_club/2">ПРУФ</a>]\n\nА сейчас я помогу тебе выйти с нуля к доходу, о '
            f'котором ты так долго мечтал. \n\nНажимай на кнопку ниже и забирай пошаговые гайды по '
            f'<b>самым жирным направлениям 2025 года 👇</b>')
    media = MediaAttachment(path='medias/main.png', type=ContentType.PHOTO)
    return {
        'media': media,
        'text': text,
        'admin': admin
    }


async def schemes_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    text = ('Снизу я собрал <b>САМЫЕ ЖИРНЫЕ</b> направления 2025 года.\n\nИменно они помогут тебе заработать первый '
            'капитал. Выбирай что по душе и начинай уже грести бабки лопатой\n\n<em><b>P.S.</b> Cхемы постоянно '
            'обновляются, включай уведомления и получай наисвежайший материал абсолютно <b>БЕСПЛАТНО</b>:</em>')
    media = MediaAttachment(path='medias/schemes_menu.png', type=ContentType.PHOTO)

    buttons = [(scheme.name, scheme.id) for scheme in await session.get_schemes()]
    buttons = [buttons[i:i + 10] for i in range(0, len(buttons), 10)]

    page = dialog_manager.dialog_data.get('page')
    if not page:
        page = 0
        dialog_manager.dialog_data['page'] = page
    current_buttons = buttons[page] if buttons else []

    not_first = False
    not_last = False
    if page != 0:
        not_first = True
    if len(buttons) and page != len(buttons) - 1:
        not_last = True
    return {
        'media': media,
        'text': text,
        'items': current_buttons,
        'schemes': bool(buttons) and len(buttons) > 1,
        'page': f'{page + 1}/{len(buttons)}',
        'not_first': not_first,
        'not_last': not_last
    }


async def pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    page = dialog_manager.dialog_data.get('page')
    action = clb.data.split('_')[0]
    if action == 'back':
        page -= 1
    else:
        page += 1
    dialog_manager.dialog_data['page'] = page
    await dialog_manager.switch_to(startSG.schemes)


async def scheme_select(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    scheme_id = int(item_id)
    messages = await session.get_scheme_messages(scheme_id)
    message = messages[0]
    keyboard = await get_scheme_keyboard(message.button, 0, scheme_id)
    await clb.bot.copy_message(
        chat_id=clb.message.chat.id,
        message_id=message.message_id,
        from_chat_id=message.chat_id,
        reply_markup=keyboard
    )


async def help_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    text = ('<b>Это особый раздел.</b>\n\nЕсли что-то не понятно или тебе нужна помощь, то смело пиши по следующему '
            'контакту (@zabota_kurt) и задавай вопрос.\n\n<em>Чтобы ускорить ответ пиши сразу полный вопрос в '
            'одном сообщении. Это значительно упрощает работу.</em>')
    media = MediaAttachment(path='medias/help_menu.png', type=ContentType.PHOTO)
    return {
        'media': media,
        'text': text
    }
