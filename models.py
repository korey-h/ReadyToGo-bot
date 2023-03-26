import json
from typing import List

from . import static_buttons as sb
from .api_handlers import get_race_detail, send_registration
from .config import REG_MESSAGE


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

    _stop_text = 'to registration'
    _finish_step = 10
    _prior_messages = {
        1: {'text': REG_MESSAGE['mess_ask_race']},
        2: {'text': REG_MESSAGE['mess_ask_name'],
            'kbd_maker': sb.race_detail_button},
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
        9: {'text': REG_MESSAGE['mess_ask_number']},
        10: {'text': _stop_text},
    }

    def _get_action(self, step: int):
        step_actions = {
            1: {'name': 'race', 'required': True},
            2: {'name': 'name', 'required': True},
            3: {'name': 'surname', 'required': True},
            4: {'name': 'patronymic', 'required': False},
            5: {'name': 'year', 'required': True},
            6: {'name': 'town', 'required': False},
            7: {'name': 'club', 'required': False},
            8: {'name': 'category', 'required': True},
            9: {'name': 'number', 'required': True},
            10: {'name': 'registration', 'required': True},
        }
        return step_actions[step]

    def _get_validator(self, step: int):
        validators = {
            1: self._race_setter,
            2: self._clipper,
            3: self._clipper,
            4: self._clipper,
            5: self._to_integer,
            6: self._clipper,
            7: self._clipper,
            8: self._to_category,
            9: self._to_integer,
        }
        return validators[step]

    def is_act_required(self):
        act = self._get_action(self.step)
        return act['required']

    def step_handler(self, data) -> List[dict]:
        validator = self._get_validator(self.step)
        res = validator(data)
        if res['error']:
            return self.mess_wrapper(res['error'])

        entry = self._get_action(self.step)['name']
        self.reg_blank[entry] = data
        self.step += 1
        return self.mess_wrapper(self.step)

    def exec(self, data):
        res = self.step_handler(self, data)
        if self.step == self._finish_step:
            return self.make_registration()
        return res

    def make_registration(self):
        res = send_registration(self.reg_blank)
        if res['status'] == 200:
            r = self.race
            bl = self.reg_blank
            cat_names = {c['id']: c['name'] for c in r['categories']}

            text = f'{r["name"]}, категория "{cat_names[bl["category"]]}",'\
                   f'номер {bl["number"]}, {bl["name"]} {bl["patronymic"]}'\
                   f' {bl["surname"]}, {bl["year"]} г.р.'
            return self.mess_wrapper({'text': text})
        elif res['status'] == 400:

            pass
        elif res['status'] == 500:
            return self.mess_wrapper(
                {'text': REG_MESSAGE['conection_error']})
        return self.mess_wrapper({'text': REG_MESSAGE['unknown_reg_error']})

    def mess_wrapper(self, step: int):
        data = self._prior_messages[step]
        text = data['text']
        maker = data.get('kbd_maker')
        keyboard = maker(self) if maker else None
        return {'text': text, 'reply_markup': keyboard}

    def _clipper(self, data) -> dict:
        data = data.strip()
        return {'data': data, 'error': None}

    def _to_integer(self, data) -> dict:
        data = data.strip()
        message = None
        try:
            data = int(data)
        except Exception:
            data = None
            message = REG_MESSAGE['not_integer']
        return {'data': data, 'error': message}

    def _to_category(self, data) -> dict:
        data = data.strip()
        message = None
        try:
            data = json.loads(data)
        except Exception:
            data = None
            message = REG_MESSAGE['not_category']
            return {'data': data, 'error': message}
        category_id = data.get('category_id')
        if not category_id:
            return {'data': category_id,
                    'error': REG_MESSAGE['no_category_data']}

        return {'data': category_id, 'error': None}

    def _race_setter(self, data) -> dict:
        detail = get_race_detail(data)
        if detail['status'] == 404:
            return {'data': None,
                    'error': REG_MESSAGE['race_not_found']}
        elif detail['status'] != 200:
            return {'data': None,
                    'error': REG_MESSAGE['conection_error']}
        self.race = detail['data']
        return {'data': self.race['id'], 'error': None}
