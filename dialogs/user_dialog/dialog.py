from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.user_dialog import getters

from states.state_groups import startSG, adminSG

user_dialog = Dialog(
    Window(
        DynamicMedia('media'),
        Format('{text}'),
        Column(
            SwitchTo(Const('ЗАБРАТЬ СХЕМЫ'), id='schemes_switcher', state=startSG.schemes),
            SwitchTo(Const('СЛУЖБА ЗАБОТЫ'), id='help_switcher', state=startSG.help),
            Start(Const('Админ панель'), id='admin', state=adminSG.start, when='admin')
        ),
        getter=getters.start_getter,
        state=startSG.start
    ),
    Window(
        DynamicMedia('media'),
        Format('{text}'),
        Group(
            Select(
                Format('{item[0]}'),
                id='schemes_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.scheme_select
            ),
            width=2
        ),
        Row(
            Button(Const('◀️'), id='back_pager', on_click=getters.pager, when='not_first'),
            Button(Format('{page}'), id='pager', when='schemes'),
            Button(Const('▶️'), id='next_pager', on_click=getters.pager, when='not_last')
        ),
        SwitchTo(Const('⬅️Назад'), id='back', state=startSG.start),
        getter=getters.schemes_getter,
        state=startSG.schemes
    ),
    Window(
        DynamicMedia('media'),
        Format('{text}'),
        Column(
            Url(Const('КОНТАКТ'), id='help_url', url=Const('https://t.me/zabota_kurt')),
        ),
        SwitchTo(Const('⬅️Назад'), id='back', state=startSG.start),
        getter=getters.help_getter,
        state=startSG.help
    )
)