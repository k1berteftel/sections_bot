from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Cancel
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.admin_dialog import getters
from states.state_groups import adminSG


admin_dialog = Dialog(
    Window(
        Const('Админ панель'),
        Column(
            Button(Const('📊 Получить статистику'), id='get_static', on_click=getters.get_static),
            SwitchTo(Const('Управление схемами'), id='schemes_switcher', state=adminSG.schemes),
            SwitchTo(Const('🛫Сделать рассылку'), id='mailing_menu_switcher', state=adminSG.mail_choose),
            SwitchTo(Const('🔗 Управление диплинками'), id='deeplinks_menu_switcher', state=adminSG.deeplink_menu),
            SwitchTo(Const('👥 Управление админами'), id='admin_menu_switcher', state=adminSG.admin_menu),
            Button(Const('📋Выгрузка базы пользователей'), id='get_users_txt', on_click=getters.get_users_txt),
        ),
        Cancel(Const('Назад'), id='close_admin'),
        state=adminSG.start
    ),
    Window(
        Const("Управление схемами"),
        Format('{text}'),
        Column(
            SwitchTo(Const('Добавить схему'), id='get_scheme_name_switcher', state=adminSG.get_scheme_name),
            SwitchTo(Const('Редактирование схем'), id='choose_scheme_switcher', state=adminSG.choose_scheme),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.schemes_getter,
        state=adminSG.schemes
    ),
    Window(
        Const('Введите названия для новой схемы'),
        TextInput(
            id='get_scheme_name',
            on_success=getters.get_scheme_name
        ),
        SwitchTo(Const('🔙 Назад'), id='back_schemes', state=adminSG.schemes),
        state=adminSG.get_scheme_name
    ),
    Window(
        Format('Введите текст сообщения <em>{number}</em> для нового раздела "{name}"'),
        MessageInput(
            func=getters.get_scheme_message,
            content_types=ContentType.ANY
        ),
        getter=getters.get_scheme_message_getter,
        state=adminSG.get_scheme_message
    ),
    Window(
        Const("Введите название для кнопки переключения на следующий раздел или же дайте названия "
              "по которому просмотр раздела закончится"),
        TextInput(
            id='get_message_button',
            on_success=getters.get_message_button
        ),
        SwitchTo(Const('🔙 Назад'), id='back_get_scheme_message', state=adminSG.get_scheme_message),
        state=adminSG.get_message_button
    ),
    Window(
        Format("В разделе уже {number} сообщений хотите сохранить раздел с данными сообщениями или "
               "продолжить добавлять сообщения?"),
        Column(
            Button(Const('➕Добавить сообщение'), id='add_message', on_click=getters.add_message_switcher),
            Button(Const('📌Сохранить раздел'), id='save_scheme', on_click=getters.save_scheme),
        ),
        SwitchTo(Const('🔙 На главное меню'), id='back_schemes', state=adminSG.schemes),
        getter=getters.confirm_scheme_getter,
        state=adminSG.confirm_scheme
    ),
    Window(
        Const('Выберите схему, которую вы хотели бы отредактировать'),
        Group(
            Select(
                Format('{item[0]}'),
                id='choose_scheme_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.scheme_selector
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back_schemes', state=adminSG.schemes),
        getter=getters.choose_scheme_getter,
        state=adminSG.choose_scheme
    ),
    Window(
        Format('Схема "{name}"\n - Сообщений в схеме: {messages}\nСсылка на раздел: <code>{deeplink}</code>'),
        Column(
            SwitchTo(Const('Изменить название'), id='change_scheme_name_switcher', state=adminSG.change_scheme_name),
            SwitchTo(Const('Просмотр сообщений'), id='watch_scheme_message_switcher', state=adminSG.scheme_message_choose),
            SwitchTo(Const('Удалить схему'), id='del_scheme_switcher', state=adminSG.del_scheme),
        ),
        SwitchTo(Const('🔙 Назад'), id='back_schemes', state=adminSG.schemes),
        getter=getters.scheme_menu_getter,
        state=adminSG.scheme_menu
    ),
    Window(
        Const('Выберите сообщение, которые вы хотели бы просмотреть'),
        Group(
            Select(
                Format('{item[0]}'),
                id='scheme_message_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.watch_message_selector
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back_scheme_menu', state=adminSG.scheme_menu),
        getter=getters.scheme_message_choose_getter,
        state=adminSG.scheme_message_choose
    ),
    Window(
        Const('Введите новое название для схемы'),
        TextInput(
            id='change_scheme_name',
            on_success=getters.change_scheme_name
        ),
        SwitchTo(Const('🔙 Назад'), id='back_scheme_menu', state=adminSG.scheme_menu),
        state=adminSG.change_scheme_name
    ),
    Window(
        Const('Введите новое сообщение для раздела схемы'),
        MessageInput(
            func=getters.change_scheme_message,
            content_types=ContentType.ANY
        ),
        SwitchTo(Const('🔙 На главное меню'), id='back_scheme_menu', state=adminSG.scheme_menu),
        state=adminSG.change_scheme_message
    ),
    Window(
        Const('Введите новое название кнопки для раздела схемы'),
        TextInput(
            id='change_scheme_button',
            on_success=getters.change_scheme_button
        ),
        SwitchTo(Const('🔙 На главное меню'), id='back_scheme_menu', state=adminSG.scheme_menu),
        state=adminSG.change_scheme_button
    ),
    Window(
        Const("Вы действительно хотите удалить схему?"),
        Row(
            Button(Const('Удалить'), id='del_scheme', on_click=getters.del_scheme),
            SwitchTo(Const('Отмена'), id='back_scheme_menu', state=adminSG.scheme_menu),
        ),
        state=adminSG.del_scheme
    ),
    Window(
        Format('🔗 *Меню управления диплинками*\n\n'
               '🎯 *Имеющиеся диплинки*:\n{links}'),
        Column(
            Button(Const('➕ Добавить диплинк'), id='add_deeplink', on_click=getters.add_deeplink),
            SwitchTo(Const('❌ Удалить диплинки'), id='del_deeplinks', state=adminSG.deeplink_del),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.deeplink_menu_getter,
        state=adminSG.deeplink_menu
    ),
    Window(
        Const('❌ Выберите диплинк для удаления'),
        Group(
            Select(
                Format('🔗 {item[0]}'),
                id='deeplink_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_deeplink
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='deeplinks_back', state=adminSG.deeplink_menu),
        getter=getters.del_deeplink_getter,
        state=adminSG.deeplink_del
    ),
    Window(
        Format('👥 *Меню управления администраторами*\n\n {admins}'),
        Column(
            SwitchTo(Const('➕ Добавить админа'), id='add_admin_switcher', state=adminSG.admin_add),
            SwitchTo(Const('❌ Удалить админа'), id='del_admin_switcher', state=adminSG.admin_del)
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.admin_menu_getter,
        state=adminSG.admin_menu
    ),
    Window(
        Const('👤 Выберите пользователя, которого хотите сделать админом\n'
              '⚠️ Ссылка одноразовая и предназначена для добавления только одного админа'),
        Column(
            Url(Const('🔗 Добавить админа (ссылка)'), id='add_admin',
                url=Format('http://t.me/share/url?url=https://t.me/kurtrobot?start={id}')),  # поменять ссылку
            Button(Const('🔄 Создать новую ссылку'), id='new_link_create', on_click=getters.refresh_url),
            SwitchTo(Const('🔙 Назад'), id='back_admin_menu', state=adminSG.admin_menu)
        ),
        getter=getters.admin_add_getter,
        state=adminSG.admin_add
    ),
    Window(
        Const('❌ Выберите админа для удаления'),
        Group(
            Select(
                Format('👤 {item[0]}'),
                id='admin_del_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_admin
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back_admin_menu', state=adminSG.admin_menu),
        getter=getters.admin_del_getter,
        state=adminSG.admin_del
    ),
    Window(
        Const('Выберите на какую аудиторию вы хотели бы сделать рассылку'),
        Column(
            Button(Const('На всех'), id='all_mail_choose', on_click=getters.mail_choose),
            Button(Const('На подписчиков'), id='subs_mail_choose', on_click=getters.mail_choose),
            Button(Const('На людей без подписки'), id='users_mail_choose', on_click=getters.mail_choose),
        ),
        SwitchTo(Const('Назад'), id='back', state=adminSG.start),
        state=adminSG.mail_choose
    ),
    Window(
        Const('Введите сообщение которое вы хотели бы разослать\n\n<b>Предлагаемый макросы</b>:'
              '\n{name} - <em>полное имя пользователя</em>'),
        MessageInput(
            content_types=ContentType.ANY,
            func=getters.get_mail
        ),
        SwitchTo(Const('Назад'), id='back', state=adminSG.start),
        state=adminSG.get_mail
    ),
    Window(
        Const('Введите дату и время в которое сообщение должно отправиться всем юзерам в формате '
              'час:минута:день:месяц\n Например: 18:00 10.02 (18:00 10-ое февраля)'),
        TextInput(
            id='get_time',
            on_success=getters.get_time
        ),
        SwitchTo(Const('Продолжить без отложки'), id='get_keyboard_switcher', state=adminSG.get_keyboard),
        SwitchTo(Const('Назад'), id='back_get_mail', state=adminSG.get_mail),
        state=adminSG.get_time
    ),
    Window(
        Const('Введите кнопки которые будут крепиться к рассылаемому сообщению\n'
              'Введите кнопки в формате:\n кнопка1 - ссылка1\nкнопка2 - ссылка2'),
        TextInput(
            id='get_mail_keyboard',
            on_success=getters.get_mail_keyboard
        ),
        SwitchTo(Const('Продолжить без кнопок'), id='confirm_mail_switcher', state=adminSG.confirm_mail),
        SwitchTo(Const('Назад'), id='back_get_time', state=adminSG.get_time),
        state=adminSG.get_keyboard
    ),
    Window(
        Const('Вы подтверждаете рассылку сообщения'),
        Row(
            Button(Const('Да'), id='start_malling', on_click=getters.start_malling),
            Button(Const('Нет'), id='cancel_malling', on_click=getters.cancel_malling),
        ),
        SwitchTo(Const('Назад'), id='back_get_keyboard', state=adminSG.get_keyboard),
        state=adminSG.confirm_mail
    ),
)