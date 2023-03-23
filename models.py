from typing import List

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from . import static_buttons as sb
from .api_handlers import get_race_detail
from .config import REG_BUTTONS, REG_MESSAGE


class User:
    def __init__(self, id):
        self.id = id
        self._commands = []

    def get_cmd_stack(self):
        if len(self._commands) > 0:
            return self._commands[-1]
        return []

    def set_cmd_stack(self, cmd_stack):
        if isinstance(cmd_stack, dict):
            self._commands.append(cmd_stack)
        else:
            keys = ('cmd_name', 'cmd', 'data', 'called_by')
            if isinstance(cmd_stack, (list, tuple)):
                s = tuple(cmd_stack)
                keys_am = len(keys)
                values = s[:keys_am] if len(s) >= keys_am else (
                    s + tuple(None for _ in range(keys_am - len(s)))
                    )
            else:
                values = (cmd_stack, cmd_stack, {}, None)
            self._commands.append(
                {key: val for key, val in zip(keys, values)}
            )

    cmd_stack = property(get_cmd_stack, set_cmd_stack)

    def clear_stack(self):
        self._commands.clear()

    def cmd_stack_pop(self):
        if len(self._commands) > 0:
            return self._commands.pop()
        return None


class RegistrProces:

    def mess_wrapper(self, step: int):
        data = self._prior_messages[step]
        text = data['text']
        maker = data.get('kbd_maker')
        keyboard = maker(self) if maker else None
        return {'text': text, 'reply_markup': keyboard}

    _prior_messages = {
        2: {'text': REG_MESSAGE['mess_ask_name']},
        3: {'text': REG_MESSAGE['mess_ask_surname']},
        4: {'text': REG_MESSAGE['mess_ask_patronymic'],
            'kbd_maker': sb.pass_keyboard},
        5: {'text': REG_MESSAGE['mess_ask_year']},
        6: {'text': REG_MESSAGE['mess_ask_town'],
            'kbd_maker': sb.pass_keyboard},
        7: {'text': REG_MESSAGE['mess_ask_club'],
            'kbd_maker': sb.pass_keyboard},
        8: {'text': REG_MESSAGE['mess_ask_category'],
            'kbd_maker': sb.category_keyboard},

    }

    def __init__(self) -> None:
        self.step = 1
        self.race = None
        self.error = None
        self._fix_list = []
        self.reg_blank = {
            'race': None,
            'category': None,
            'name': '',
            'surname': '',
            'patronymic': '',
            'number': None,
            'year': None,
            'club': '',
            'town': ''
        }

    def get_race_info(self, race_id) -> List[dict]:
        detail = get_race_detail(race_id)
        if detail['status'] == 404:
            return {'text': REG_MESSAGE['race_not_found']}
        elif detail['status'] != 200:
            return {'text': REG_MESSAGE['conection_error']}
        self.race = detail['data']
        r = self.race
        self.reg_blank['race'] = r['id']
        self.step = 2
        mess_ask_name = self.mess_wrapper(self.step)

        btn_race_detail = InlineKeyboardButton(
            text=REG_BUTTONS['race_detail'],
            callback_data=f'race_detai:{r["id"]}')
        keyboard = InlineKeyboardMarkup().add(btn_race_detail)
        mess_about = self.mess_wrapper(
            f'{r["name"]}, {r["date"]}',
            keyboard)

        return (mess_about, mess_ask_name)

    def set_name(self, data: str):
        name = data.strip()
        self.reg_blank['name'] = name
        if not self._fix_list:
            self.step = 3
        else:
            self.step = self._fix_list.pop(0)
        mess = self.mess_wrapper(self.step)
        return (mess, )

    def set_surname(self, data: str):
        surname = data.strip()
        self.reg_blank['surname'] = surname
        if not self._fix_list:
            self.step = 4
        else:
            self.step = self._fix_list.pop(0)
        mess = self.mess_wrapper(self.step)
        return (mess, )

    def set_patronymic(self, data: str):
        patronymic = data.strip()
        self.reg_blank['patronymic'] = patronymic
        if not self._fix_list:
            self.step = 5
        else:
            self.step = self._fix_list.pop(0)
        mess = self.mess_wrapper(self.step)
        return (mess, )

    def set_year(self, data):
        year = data.strip()
        self.reg_blank['year'] = year
        if not self._fix_list:
            self.step = 6
        else:
            self.step = self._fix_list.pop(0)
        mess = self.mess_wrapper(self.step)
        return (mess, )

    def set_town(self, data):
        town = data.strip()
        self.reg_blank['town'] = town
        if not self._fix_list:
            self.step = 7
        else:
            self.step = self._fix_list.pop(0)
        mess = self.mess_wrapper(self.step)
        return (mess, )

    def set_club(self, data):
        club = data.strip()
        self.reg_blank['town'] = club
        if not self._fix_list:
            self.step = 8
        else:
            self.step = self._fix_list.pop(0)
        mess = self.mess_wrapper(self.step)
        return (mess, )

    def set_category(self, data):
        category_ids = [cat.id for cat in self.race['categories']]
        if data not in category_ids:
            return {'text': REG_MESSAGE['category_not_found']}
        category = data.strip()
        self.reg_blank['category'] = category
        if not self._fix_list:
            self.step = 9
        else:
            self.step = self._fix_list.pop(0)
        mess = self.mess_wrapper(self.step)
        return (mess, )

    def set_number(self, data):
        pass

    def make_registration(self):
        pass

    __step_actions__ = {
        1: {'handler': get_race_info, 'required': True},
        2: {'handler': set_name, 'required': True},
        3: {'handler': set_surname, 'required': True},
        4: {'handler': set_patronymic, 'required': False},
        5: {'handler': set_year, 'required': True},
        6: {'handler': set_town, 'required': False},
        7: {'handler': set_club, 'required': False},
        8: {'handler': set_category, 'required': True},
        9: {'handler': set_number, 'required': True},
        10: {'handler': make_registration, 'required': True},
    }
